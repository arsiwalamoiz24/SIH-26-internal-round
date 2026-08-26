"use client";

import { useState, useMemo, useRef, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, useTexture } from "@react-three/drei";
import { PRIMARY, CANDIDATES } from "@/data/prism";
import * as THREE from "three";

// ── 3D Parametric Crater ──────────────────────────────────────────
// Rim shape comes from the candidate's real (non-circular) PSR boundary
// polygon (public/assets/prism/psr_boundary/{id}.json, exported locally from
// data/raw/psr_south/*.shp — no network needed). Height everywhere (inside
// AND around the crater, not just the bowl) comes from each candidate's real
// wide LOLA elevation grid (public/assets/prism/elevation/*_wide.json, a 9km-
// radius window) — real surrounding terrain instead of a flat synthetic apron.
// The mesh is textured with a *cropped single panel* pulled from whichever 2D
// layer is active (hazard/terrain science plots have their own tightly-cropped
// no-title/no-colorbar export — see hazard_only.png / elevation_only.png —
// so the texture is never the old multi-panel wallpaper), scaled so the
// texture's real-world footprint lines up with the mesh's own real-world size.
type BoundaryJSON = { boundary_xy_m: [number, number][] };
type ElevationGridJSON = {
  elevationGridRelativeM: number[][];
  window_half_m: number;
  grid_size: number;
};

// Real-world half-width (m) covered by each texture source, so its UVs can be
// scaled to match the mesh's own real-world footprint instead of guessed
// offset/repeat constants. hazard_only crops come from hazard_map_pipeline.py /
// hazard_map_shortlist_pipeline.py (BUFFER_M=5000); elevation_only crops come
// from the narrow real elevation grid (half_m=3300); ShadowCam crops use a
// comparable ~5km extraction.
const TEXTURE_SOURCE_HALF_M: Record<string, number> = {
  hazard: 5000,
  terrain: 3300,
  shadowcam: 5000,
};

const MESH_HALF = 10; // PlaneGeometry(20,20) spans -10..10
const AVG_RIM_UNITS = 8.2; // matches the previous constant circular rim radius
const ANGLE_BUCKETS = 360;

function buildRimLookup(boundaryPoints: [number, number][]) {
  let maxR = 0;
  for (const [x, y] of boundaryPoints) {
    const r = Math.hypot(x, y);
    if (r > maxR) maxR = r;
  }
  const scale = maxR > 0 ? AVG_RIM_UNITS / maxR : 1;
  const scaled = boundaryPoints.map(([x, y]) => [x * scale, y * scale] as [number, number]);

  // Ray-cast from the mesh center at 360 angles to find the true rim radius
  // in every direction (irregular polygon, not a constant circle radius).
  const rimByAngle = new Float32Array(ANGLE_BUCKETS).fill(AVG_RIM_UNITS);
  for (let i = 0; i < ANGLE_BUCKETS; i++) {
    const theta = (i / ANGLE_BUCKETS) * Math.PI * 2;
    const dx = Math.cos(theta), dz = Math.sin(theta);
    let best = Infinity;
    for (let j = 0; j < scaled.length; j++) {
      const [ax, az] = scaled[j];
      const [bx, bz] = scaled[(j + 1) % scaled.length];
      const ex = bx - ax, ez = bz - az;
      const det = ex * dz - ez * dx;
      if (Math.abs(det) < 1e-9) continue;
      const t = (-ax * ez + ex * az) / det;
      const s = (dx * az - dz * ax) / det;
      if (t > 0.01 && s >= 0 && s <= 1 && t < best) best = t;
    }
    if (Number.isFinite(best)) rimByAngle[i] = best;
  }
  return { rimByAngle, scale };
}

function sampleElevationGrid(grid: number[][], gridSize: number, u: number, v: number) {
  const cu = Math.min(Math.max(u, 0), gridSize - 1.001);
  const cv = Math.min(Math.max(v, 0), gridSize - 1.001);
  const u0 = Math.floor(cu), v0 = Math.floor(cv);
  const u1 = u0 + 1, v1 = v0 + 1;
  const fu = cu - u0, fv = cv - v0;
  const g00 = grid[v0][u0], g10 = grid[v0][u1], g01 = grid[v1][u0], g11 = grid[v1][u1];
  const top = g00 + (g10 - g00) * fu;
  const bottom = g01 + (g11 - g01) * fu;
  return top + (bottom - top) * fv;
}

// 1x1 transparent pixel — keeps useTexture's hook call unconditional even
// when the active layer has no real cropped texture to show (radar, pending
// raw SAR source data for non-primary candidates).
const BLANK_TEXTURE_URL =
  "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=";

function CraterMesh({
  candidateId, elevRange, activeLayer, shadowcamUrl,
}: {
  candidateId: string;
  elevRange: number;
  activeLayer: "shadowcam" | "radar" | "hazard" | "terrain";
  shadowcamUrl: string;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [boundary, setBoundary] = useState<BoundaryJSON | null>(null);
  const [wideGrid, setWideGrid] = useState<ElevationGridJSON | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch(`/assets/prism/psr_boundary/${candidateId}.json`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => { if (!cancelled) setBoundary(data); })
      .catch(() => { if (!cancelled) setBoundary(null); });
    // Wide (9km-radius) real LOLA elevation grid — now available for all 7
    // candidates — drives height everywhere on the mesh, not just the bowl,
    // so real surrounding terrain shows around the crater rim.
    fetch(`/assets/prism/elevation/${candidateId}_real_elevation_grid_wide.json`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => { if (!cancelled) setWideGrid(data); })
      .catch(() => { if (!cancelled) setWideGrid(null); });
    return () => { cancelled = true; };
  }, [candidateId]);

  // Slow auto-rotation for cinematic feel
  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.03;
    }
  });

  const { rimByAngle, scale } = useMemo(() => {
    return boundary
      ? buildRimLookup(boundary.boundary_xy_m)
      : { rimByAngle: new Float32Array(ANGLE_BUCKETS).fill(AVG_RIM_UNITS), scale: 1 };
  }, [boundary]);

  const geometry = useMemo(() => {
    const geo = new THREE.PlaneGeometry(20, 20, 160, 160);
    geo.rotateX(-Math.PI / 2);

    const depthScale = (elevRange / 1742) * 3.2;
    // Meters-of-real-relief -> mesh-Y-units, tied to this candidate's own
    // documented elevation range (not the wide grid's own min/max, which can
    // be dominated by distant terrain far outside the crater itself).
    const metersToMeshY = depthScale / (elevRange / 2);
    const positions = geo.attributes.position;

    for (let i = 0; i < positions.count; i++) {
      const x = positions.getX(i);
      const z = positions.getZ(i);
      const dist = Math.sqrt(x * x + z * z);

      let theta = Math.atan2(z, x);
      if (theta < 0) theta += Math.PI * 2;
      const bucket = Math.floor((theta / (Math.PI * 2)) * ANGLE_BUCKETS) % ANGLE_BUCKETS;
      const rim = rimByAngle[bucket];
      const nd = dist / rim; // 0 at center, 1 at the true (non-circular) rim, >1 outside

      let y = 0;
      let usedRealGrid = false;

      if (wideGrid) {
        const halfM = wideGrid.window_half_m;
        const gridSize = wideGrid.grid_size;
        const realX = x / scale, realZ = z / scale; // mesh units -> meters
        const u = ((realX + halfM) / (2 * halfM)) * (gridSize - 1);
        const v = ((realZ + halfM) / (2 * halfM)) * (gridSize - 1);
        if (u >= 0 && u <= gridSize - 1 && v >= 0 && v <= gridSize - 1) {
          y = sampleElevationGrid(wideGrid.elevationGridRelativeM, gridSize, u, v) * metersToMeshY;
          usedRealGrid = true;
        }
      }

      if (!usedRealGrid) {
        // Fallback synthetic bowl — only used before the real grid has loaded,
        // or if it's ever unavailable for a candidate.
        if (nd < 1) {
          const parabola = 1 - nd * nd;
          const gaussian = Math.exp(-nd * nd * 3);
          y = -depthScale * (parabola * 0.6 + gaussian * 0.4);
        } else {
          const drop = Math.min((nd - 1) * 0.8, 0.6);
          y = -depthScale * drop * 0.4;
        }
      }

      // Rim: a slight raised ring right at the true boundary, so the crater
      // outline still reads clearly against the real surrounding terrain.
      if (nd > 0.9 && nd < 1.08) {
        const t = Math.min(Math.max((nd - 0.9) / 0.18, 0), 1);
        y += depthScale * 0.15 * Math.sin(t * Math.PI);
      }

      // Small surface jitter — real DEM already carries its own roughness at
      // its native resolution, so this is subtle texture, not shape.
      y += (Math.random() - 0.5) * (nd < 1 ? 0.05 : 0.03);

      positions.setY(i, y);
    }

    geo.computeVertexNormals();
    return geo;
  }, [elevRange, wideGrid, rimByAngle, scale]);

  // Texture: a single cropped science panel matching the active 2D layer
  // (never the old multi-panel wallpaper), scaled so its real-world footprint
  // lines up with the mesh's own real-world size.
  const textureUrl =
    activeLayer === "shadowcam" ? shadowcamUrl :
    activeLayer === "hazard" ? `/assets/prism/hazard_only/${candidateId}.png` :
    activeLayer === "terrain" ? `/assets/prism/elevation_only/${candidateId}.png` :
    BLANK_TEXTURE_URL; // radar: no cropped texture yet — raw SAR source pending

  const texture = useTexture(textureUrl);
  texture.wrapS = THREE.ClampToEdgeWrapping;
  texture.wrapT = THREE.ClampToEdgeWrapping;
  const halfM = TEXTURE_SOURCE_HALF_M[activeLayer] ?? 5000;
  const meshHalfExtentM = MESH_HALF / (scale || 1);
  const repeatFrac = Math.min(meshHalfExtentM / halfM, 1);
  texture.offset.set((1 - repeatFrac) / 2, (1 - repeatFrac) / 2);
  texture.repeat.set(repeatFrac, repeatFrac);
  texture.needsUpdate = true;

  return (
    <mesh ref={meshRef} geometry={geometry}>
      <meshStandardMaterial
        map={activeLayer === "radar" ? null : texture}
        color={activeLayer === "radar" ? "#8c877e" : "#ffffff"}
        roughness={0.94}
        metalness={0.02}
      />
    </mesh>
  );
}

export default function TerrainPage() {
  const [activeLayer, setActiveLayer] = useState<"shadowcam" | "radar" | "hazard" | "terrain">("hazard");
  const [selectedCandidateId, setSelectedCandidateId] = useState<string>("SP_840980_0797630");

  const selectedCandidate = CANDIDATES.find(c => c.id === selectedCandidateId) || CANDIDATES[0];

  // Radar composites only exist for the primary candidate (raw DFSAR source
  // data for the other 6 isn't available yet) — auto-fallback off that tab
  // instead of silently showing the primary candidate's image.
  useEffect(() => {
    if (!selectedCandidate.isPrimary && activeLayer === "radar") {
      setActiveLayer("hazard");
    }
  }, [selectedCandidate, activeLayer]);

  const shadowcamUrl = selectedCandidate.id === "SP_840980_0797630"
    ? PRIMARY.images.shadowcam
    : selectedCandidate.shadowcamImage;

  const getLayerImage = () => {
    if (selectedCandidate.id === "SP_840980_0797630") {
      switch (activeLayer) {
        case "shadowcam": return PRIMARY.images.shadowcam;
        case "radar":     return PRIMARY.images.radar;
        case "hazard":    return PRIMARY.images.hazard;
        case "terrain":   return PRIMARY.images.terrain;
        default:          return PRIMARY.images.hazard;
      }
    } else {
      switch (activeLayer) {
        case "shadowcam": return selectedCandidate.shadowcamImage;
        case "hazard":    return selectedCandidate.hazardImage;
        case "terrain":   return selectedCandidate.terrainImage;
        case "radar":     return selectedCandidate.hazardImage; // radar unavailable — see useEffect fallback above
        default:          return selectedCandidate.hazardImage;
      }
    }
  };

  return (
    <main style={{ minHeight: "100dvh", paddingTop: "var(--nav-h)", background: "var(--void)", display: "flex", flexDirection: "column" }}>

      <div style={{ flex: 1, display: "grid", gridTemplateColumns: "1fr 1fr", borderTop: "1px solid var(--border)" }}>

        {/* Left: 2D Hazard & Terrain Layers */}
        <section style={{ position: "relative", borderRight: "1px solid var(--border)", display: "flex", flexDirection: "column", background: "var(--surface)" }}>

          <div style={{ padding: "32px 40px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: "16px" }}>
            <div>
              <div className="label-caps" style={{ marginBottom: "8px" }}>2D Map Layers</div>
              <h1 style={{ fontFamily: "var(--font-display)", fontSize: "24px", color: "var(--text-primary)", margin: 0, letterSpacing: "-0.01em" }}>
                Hazard Classification
              </h1>
            </div>

            {/* Layer toggles */}
            <div>
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                {(["hazard", "terrain", "shadowcam", "radar"] as const).map(layer => {
                  const disabled = layer === "radar" && !selectedCandidate.isPrimary;
                  return (
                    <button
                      key={layer}
                      onClick={() => !disabled && setActiveLayer(layer)}
                      disabled={disabled}
                      title={disabled ? "Radar composite available for primary target only" : undefined}
                      style={{
                        padding: "6px 12px",
                        fontFamily: "var(--font-mono)",
                        fontSize: "10px",
                        letterSpacing: "0.1em",
                        textTransform: "uppercase",
                        fontWeight: activeLayer === layer ? 700 : 400,
                        background: activeLayer === layer ? "var(--text-primary)" : "transparent",
                        color: disabled ? "var(--text-muted)" : activeLayer === layer ? "var(--void)" : "var(--text-secondary)",
                        border: `1px solid ${activeLayer === layer ? "transparent" : "var(--border)"}`,
                        borderRadius: "4px",
                        cursor: disabled ? "not-allowed" : "pointer",
                        opacity: disabled ? 0.45 : 1,
                        transition: "all 0.2s ease",
                      }}
                    >
                      {layer}
                    </button>
                  );
                })}
              </div>
              {!selectedCandidate.isPrimary && (
                <div style={{ marginTop: "8px", fontFamily: "var(--font-mono)", fontSize: "9px", color: "var(--text-muted)", letterSpacing: "0.06em", textAlign: "right" }}>
                  Radar composite available for primary target only — pending additional source data.
                </div>
              )}
            </div>
          </div>

          {/* Candidate dropdown in the 2D panel too */}
          <div style={{ padding: "16px 40px", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", gap: "12px" }}>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", letterSpacing: "0.1em", textTransform: "uppercase" }}>Candidate</span>
            <select
              value={selectedCandidateId}
              onChange={(e) => setSelectedCandidateId(e.target.value)}
              style={{
                background: "transparent",
                border: "1px solid var(--border)",
                color: "var(--text-primary)",
                padding: "4px 8px",
                borderRadius: "4px",
                fontFamily: "var(--font-mono)",
                fontSize: "11px",
                cursor: "pointer",
              }}
            >
              {CANDIDATES.map(c => (
                <option key={c.id} value={c.id} style={{ background: "var(--surface)" }}>
                  {c.label} {c.isPrimary ? "(Primary)" : ""}
                </option>
              ))}
            </select>
          </div>

          <div style={{ flex: 1, position: "relative", padding: "32px 40px", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <div style={{ width: "100%", maxWidth: "560px", position: "relative", border: "1px solid var(--border)", borderRadius: "4px", overflow: "hidden", background: "#000" }}>
              <img
                key={getLayerImage()}
                src={getLayerImage()}
                alt={`${activeLayer} map`}
                style={{ width: "100%", display: "block", objectFit: "contain", transition: "opacity 0.3s ease" }}
              />
            </div>
          </div>

          {/* Legend for Hazard Map */}
          {activeLayer === "hazard" && (
            <div style={{ padding: "16px 40px", borderTop: "1px solid var(--border)", display: "flex", gap: "20px", background: "rgba(255,255,255,0.01)", flexWrap: "wrap" }}>
              {[
                { color: "var(--signal-high)", label: "Safe (<10°)" },
                { color: "var(--signal-warn)", label: "Caution (10–20°)" },
                { color: "var(--signal-flag)", label: "Hazard (>20°)" },
              ].map(({ color, label }) => (
                <div key={label} style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <div style={{ width: "10px", height: "10px", background: color, borderRadius: "2px" }} />
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.08em" }}>{label}</span>
                </div>
              ))}
            </div>
          )}

        </section>

        {/* Right: 3D Visualization */}
        <section style={{ position: "relative", display: "flex", flexDirection: "column" }}>
          {/* HUD overlay */}
          <div style={{
            position: "absolute", top: 0, left: 0, right: 0, zIndex: 10,
            padding: "32px 40px",
            display: "flex", justifyContent: "space-between", alignItems: "flex-start",
            pointerEvents: "none",
          }}>
            <div style={{ pointerEvents: "auto" }}>
              <div className="label-caps" style={{ marginBottom: "6px" }}>3D Topography</div>
              <h1 style={{ fontFamily: "var(--font-display)", fontSize: "20px", color: "var(--text-primary)", margin: "0 0 12px", letterSpacing: "-0.01em" }}>
                LOLA Derived Surface
              </h1>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "4px" }}>
                Drag to orbit · Scroll to zoom
              </div>
            </div>

            <div style={{ textAlign: "right" }}>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "13px", color: "var(--text-primary)", marginBottom: "2px" }}>
                Relief: {selectedCandidate.terrain.elevRange.toFixed(0)}m
              </div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                {selectedCandidate.terrain.elevMin}m → {selectedCandidate.terrain.elevMax}m
              </div>
            </div>
          </div>

          {/* 3D Canvas */}
          <div style={{ flex: 1, position: "relative", cursor: "grab", minHeight: "400px" }}>
            <Canvas camera={{ position: [12, 9, 12], fov: 42 }}>
              {/* Cinematic lighting */}
              <ambientLight intensity={0.9} />
              {/* Primary key light — slightly warm */}
              <directionalLight position={[8, 14, 6]} intensity={3.0} color="#ffe8d0" castShadow />
              {/* Fill light — cool from opposite side */}
              <directionalLight position={[-6, 6, -8]} intensity={1.2} color="#8aabcf" />
              {/* Subtle rim light from below-front */}
              <directionalLight position={[0, -4, 10]} intensity={0.4} color="#c4a268" />

              {/* Key: remount with new key when candidate changes */}
              <CraterMesh
                key={selectedCandidate.id}
                candidateId={selectedCandidate.id}
                elevRange={selectedCandidate.terrain.elevRange}
                activeLayer={activeLayer}
                shadowcamUrl={shadowcamUrl}
              />

              <OrbitControls
                enablePan={false}
                maxPolarAngle={Math.PI / 2 - 0.02}
                minDistance={6}
                maxDistance={28}
                autoRotate={false}
              />

              {/* Floor grid */}
              <gridHelper args={[24, 24, 0x3E6B9A20, 0x1A213010]} position={[0, -3.5, 0]} />
            </Canvas>
          </div>

          {/* Bottom info bar */}
          <div style={{ padding: "14px 40px", borderTop: "1px solid var(--border)", background: "var(--surface)", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
              Parametric geometry — derived from LOLA DEM statistics · Vert. exaggeration 1.5×
            </span>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--amber)", letterSpacing: "0.08em" }}>
              {selectedCandidate.label}
            </span>
          </div>
        </section>

      </div>

      <style>{`
        @media (max-width: 1024px) {
          main > div {
            grid-template-columns: 1fr !important;
            grid-template-rows: auto 520px;
          }
        }
      `}</style>
    </main>
  );
}
