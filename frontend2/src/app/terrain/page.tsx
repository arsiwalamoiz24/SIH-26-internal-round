"use client";

import { useState, useMemo, useRef, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, useTexture } from "@react-three/drei";
import { PRIMARY, CANDIDATES, FAUSTINI, CABEUS, spIdLabel } from "@/data/prism";
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

function CraterMesh({
  candidateId, elevRange, activeLayer, shadowcamUrl, textureHalfM,
}: {
  candidateId: string;
  elevRange: number;
  activeLayer: "shadowcam" | "radar" | "hazard" | "terrain";
  shadowcamUrl?: string;
  // Real per-layer crop buffer for this specific site, when it differs from
  // the fixed defaults (see TEXTURE_SOURCE_HALF_M) -- e.g. Faustini/Cabeus's
  // real PSR polygons are much bigger than the 7 screened candidates', so
  // their hazard/terrain crops were regenerated at a bigger real buffer,
  // while their real ShadowCam crop is a normal single-frame ~1.5km window
  // (an orbital swath can't be arbitrarily widened the way a LOLA DEM read
  // can) -- far smaller than their crater, unlike the other 7 candidates.
  textureHalfM?: Partial<Record<"hazard" | "terrain" | "shadowcam", number>>;
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

  const depthScale = (elevRange / 1742) * 3.2;
  // Meters-of-real-relief -> mesh-Y-units, tied to this candidate's own
  // documented elevation range (not the wide grid's own min/max, which can
  // be dominated by distant terrain far outside the crater itself).
  const metersToMeshY = depthScale / (elevRange / 2);

  // Real terrain height at one mesh-space (x,z) point -- pulled out of the
  // geometry loop below so the ShadowCam decal (a separate small mesh, see
  // below) can sample the same real elevation grid to sit on the surface
  // instead of floating at a guessed height.
  const sampleHeight = (x: number, z: number): number => {
    if (wideGrid) {
      const halfM = wideGrid.window_half_m;
      const gridSize = wideGrid.grid_size;
      const realX = x / scale, realZ = z / scale;
      const u = ((realX + halfM) / (2 * halfM)) * (gridSize - 1);
      const v = ((realZ + halfM) / (2 * halfM)) * (gridSize - 1);
      if (u >= 0 && u <= gridSize - 1 && v >= 0 && v <= gridSize - 1) {
        return sampleElevationGrid(wideGrid.elevationGridRelativeM, gridSize, u, v) * metersToMeshY;
      }
    }
    return 0;
  };

  const geometry = useMemo(() => {
    const geo = new THREE.PlaneGeometry(20, 20, 160, 160);
    geo.rotateX(-Math.PI / 2);

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

  const meshHalfExtentM = MESH_HALF / (scale || 1);

  // A single real ShadowCam frame is a normal ~1.5km-half orbital crop --
  // correct and real, but far smaller than Faustini/Cabeus's ~19km-wide mesh
  // (the other 7 candidates' craters are close enough in size to their crop
  // that texturing the whole mesh with it is reasonable). Stretching that
  // small patch to fill the whole mesh would misrepresent it as full
  // coverage; showing it at true scale via UV clamping instead bleeds the
  // crop's own border pixel across the rest of the mesh (a smeared, glitchy-
  // looking artifact, not actually a fix). So for that specific mismatch,
  // don't texture the terrain mesh with ShadowCam at all -- show the real
  // hazard classification underneath (still real per-site context, not
  // blank) and place the real ShadowCam photo as a separate, correctly-
  // scaled, correctly-positioned flat panel resting on the terrain, the way
  // a real photo inset would sit on a map, rather than wallpapering it.
  const shadowcamHalfM = textureHalfM?.shadowcam;
  const showShadowcamAsDecal =
    activeLayer === "shadowcam" &&
    !!shadowcamHalfM &&
    meshHalfExtentM / shadowcamHalfM > 1.3;
  const baseLayer = showShadowcamAsDecal ? "hazard" : activeLayer;

  // Texture: a single cropped science panel matching the active 2D layer
  // (never the old multi-panel wallpaper), scaled so its real-world footprint
  // lines up with the mesh's own real-world size.
  const textureUrl =
    baseLayer === "shadowcam" && shadowcamUrl ? shadowcamUrl :
    baseLayer === "hazard" ? `/assets/prism/hazard_only/${candidateId}.png` :
    baseLayer === "terrain" ? `/assets/prism/elevation_only/${candidateId}.png` :
    baseLayer === "radar" ? `/assets/prism/radar_only/${candidateId}.png` :
    `/assets/prism/hazard_only/${candidateId}.png`;

  const texture = useTexture(textureUrl);
  texture.wrapS = THREE.ClampToEdgeWrapping;
  texture.wrapT = THREE.ClampToEdgeWrapping;
  // radar_only crops come from radar_pipeline.py's own PSR-bbox + 1000m buffer
  // window (not a fixed BUFFER_M like hazard/terrain), so its real-world
  // half-width varies per candidate — derive it from the same rim polygon
  // already loaded for the mesh geometry instead of a fixed constant.
  const halfM = baseLayer === "radar"
    ? (scale > 0 ? AVG_RIM_UNITS / scale + 1000 : 5000)
    : (textureHalfM?.[baseLayer as "hazard" | "terrain" | "shadowcam"] ?? TEXTURE_SOURCE_HALF_M[baseLayer] ?? 5000);
  const repeatFrac = Math.min(meshHalfExtentM / halfM, 1);
  texture.offset.set((1 - repeatFrac) / 2, (1 - repeatFrac) / 2);
  texture.repeat.set(repeatFrac, repeatFrac);
  texture.needsUpdate = true;

  // Decal texture load is unconditional (hooks can't be conditional) but only
  // ever rendered when showShadowcamAsDecal is true; falls back to the base
  // texture's own URL (already loading) rather than an empty string when
  // there's no real shadowcamUrl for this site.
  const decalTexture = useTexture(shadowcamUrl || textureUrl);
  const decalHalfMeshUnits = shadowcamHalfM ? shadowcamHalfM * scale : 0;
  const decalY = sampleHeight(0, 0) + 0.04;

  return (
    <group>
      <mesh ref={meshRef} geometry={geometry}>
        <meshStandardMaterial map={texture} color="#ffffff" roughness={0.94} metalness={0.02} />
      </mesh>

      {showShadowcamAsDecal && decalHalfMeshUnits > 0 && (
        <mesh position={[0, decalY, 0]} rotation={[-Math.PI / 2, 0, 0]} renderOrder={1}>
          <planeGeometry args={[decalHalfMeshUnits * 2, decalHalfMeshUnits * 2]} />
          <meshBasicMaterial map={decalTexture} toneMapped={false} />
        </mesh>
      )}
    </group>
  );
}

type TerrainSite = {
  id: string;
  label: string;
  dropdownLabel: string;
  isPrimary: boolean;
  isFeatured?: boolean;
  terrain: { elevMin: number; elevMax: number; elevRange: number };
  hazardImage: string;
  terrainImage: string;
  radarImage: string;
  shadowcamImage?: string;
  textureHalfM?: Partial<Record<"hazard" | "terrain" | "shadowcam", number>>;
};

// Faustini and Cabeus: featured external-validation sites (real, independently
// published ice evidence — LCROSS direct detection at Cabeus, M3 spectral
// detection at Faustini), not part of PRISM's own 7-candidate screening.
// Real single-frame ShadowCam crops now exist for both (PRISM/src/
// shadowcam_featured_sites.py, real ASU/im-ldi PDS archive search).
// Listed first below (not a separate dropdown subsection) like any other site.
const FEATURED_SITES: TerrainSite[] = [FAUSTINI, CABEUS].map((s) => ({
  id: s.id, label: s.label, dropdownLabel: `${spIdLabel(s.id)} ${s.label}`, isPrimary: false, isFeatured: true,
  terrain: s.terrain, hazardImage: s.hazardImage, terrainImage: s.terrainImage, radarImage: s.radarImage,
  shadowcamImage: s.shadowcamImage,
  textureHalfM: s.textureHalfM,
}));

const ALL_SITES: TerrainSite[] = [
  ...FEATURED_SITES,
  ...CANDIDATES.map((c): TerrainSite => ({
    id: c.id, label: c.label, dropdownLabel: c.isPrimary ? `${c.label} (Primary)` : c.label,
    isPrimary: c.isPrimary, terrain: c.terrain,
    hazardImage: c.isPrimary ? PRIMARY.images.hazard : c.hazardImage,
    terrainImage: c.isPrimary ? PRIMARY.images.terrain : c.terrainImage,
    radarImage: c.isPrimary ? PRIMARY.images.radar : c.radarImage,
    shadowcamImage: c.isPrimary ? PRIMARY.images.shadowcam : c.shadowcamImage,
    // The 6 non-primary candidates' hazard_only/elevation_only crops were
    // regenerated at a real 5000m buffer (PRISM/outputs/objective2/shortlist/
    // *_terrain_stats.json: window_buffer_m=5000), same as hazard's own
    // default -- but the fixed TEXTURE_SOURCE_HALF_M.terrain=3300 below was
    // tuned for the primary's own narrower 3300m crop (export_elevation_
    // only_crops.py), so without this override their terrain-layer texture
    // was reading the wrong real-world footprint and rendering over-zoomed.
    textureHalfM: c.isPrimary ? undefined : { hazard: 5000, terrain: 5000 },
  })),
];

export default function TerrainPage() {
  const [activeLayer, setActiveLayer] = useState<"shadowcam" | "radar" | "hazard" | "terrain">("hazard");
  const [selectedCandidateId, setSelectedCandidateId] = useState<string>("SP_840980_0797630");

  const selectedCandidate = ALL_SITES.find(c => c.id === selectedCandidateId) || ALL_SITES[0];
  const hasShadowcam = !!selectedCandidate.shadowcamImage;

  // No ShadowCam imagery for Faustini/Cabeus — fall back off that tab instead
  // of showing a broken image.
  useEffect(() => {
    if (!hasShadowcam && activeLayer === "shadowcam") {
      setActiveLayer("hazard");
    }
  }, [hasShadowcam, activeLayer]);

  const shadowcamUrl = selectedCandidate.shadowcamImage;

  // Real individual per-metric crops (PRISM/src/split_hazard_terrain_panels.py,
  // split_radar_panels.py) -- one file per metric, re-derived from the same
  // LDEM/DFSAR reads as each layer's composite figure, instead of squeezing
  // one wide multi-panel strip into a single small box. Panel lists mirror
  // each composite's own real panels exactly (hazard: slope/roughness/
  // illumination/combined; terrain: slope/elevation/TRI; radar: Y4R RGB/
  // Pv/CPR/SERD) -- present for all 9 sites.
  const panel = (metric: "pv" | "cpr" | "serd" | "tratio" | "slope" | "roughness" | "illum" | "tri") =>
    `/assets/prism/panels/${selectedCandidate.id}_${metric}_only.png`;

  const layerPanels: { src: string; label: string }[] =
    activeLayer === "shadowcam"
      ? [{ src: selectedCandidate.shadowcamImage ?? "", label: "ShadowCam" }]
      : activeLayer === "hazard"
      ? [
          { src: panel("slope"), label: "Slope" },
          { src: panel("roughness"), label: "Roughness (RMS)" },
          { src: panel("illum"), label: "Illumination" },
          { src: selectedCandidate.hazardImage, label: "Combined Hazard" },
        ]
      : activeLayer === "terrain"
      ? [
          { src: `/assets/prism/elevation_only/${selectedCandidate.id}.png`, label: "Elevation" },
          { src: panel("slope"), label: "Slope" },
          { src: panel("tri"), label: "Roughness (TRI)" },
        ]
      : [
          { src: `/assets/prism/radar_only/${selectedCandidate.id}.png`, label: "Y4R RGB" },
          { src: panel("pv"), label: "Pv" },
          { src: panel("cpr"), label: "CPR" },
          { src: panel("serd"), label: "SERD" },
        ];

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
                  const disabled = layer === "shadowcam" && !hasShadowcam;
                  return (
                    <button
                      key={layer}
                      onClick={() => !disabled && setActiveLayer(layer)}
                      disabled={disabled}
                      title={disabled ? "ShadowCam imagery not available for this reference site" : undefined}
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
                        opacity: disabled ? 0.4 : 1,
                        transition: "all 0.2s ease",
                      }}
                    >
                      {layer}
                    </button>
                  );
                })}
              </div>
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
              {ALL_SITES.map(s => (
                <option key={s.id} value={s.id} style={{ background: "var(--surface)" }}>
                  {s.dropdownLabel}
                </option>
              ))}
            </select>
          </div>

          <div style={{ flex: 1, position: "relative", padding: "32px 40px", display: "flex", alignItems: "center", justifyContent: "center", overflow: "auto" }}>
            <div
              key={activeLayer}
              style={{
                width: "100%",
                maxWidth: "640px",
                display: "grid",
                gridTemplateColumns: layerPanels.length > 1 ? "1fr 1fr" : "1fr",
                gap: "10px",
              }}
            >
              {layerPanels.map((p) => (
                <div key={p.label} style={{ position: "relative", border: "1px solid var(--border)", borderRadius: "4px", overflow: "hidden", background: "#000" }}>
                  <img
                    src={p.src}
                    alt={p.label}
                    style={{ width: "100%", aspectRatio: "1/1", display: "block", objectFit: "cover" }}
                  />
                  <span
                    style={{
                      position: "absolute", bottom: "6px", left: "6px",
                      fontFamily: "var(--font-mono)", fontSize: "8px", letterSpacing: "0.08em", textTransform: "uppercase",
                      color: "#fff", background: "rgba(0,0,0,0.55)", padding: "2px 6px", borderRadius: "2px",
                    }}
                  >
                    {p.label}
                  </span>
                </div>
              ))}
            </div>

            {activeLayer === "shadowcam" && selectedCandidate.textureHalfM?.shadowcam && (
              <div
                style={{
                  marginTop: "12px",
                  fontFamily: "var(--font-mono)",
                  fontSize: "9px",
                  color: "var(--text-muted)",
                  lineHeight: 1.5,
                  maxWidth: "640px",
                }}
              >
                Real single-frame ShadowCam pass ({(selectedCandidate.textureHalfM.shadowcam * 2 / 1000).toFixed(1)}km
                across) — a real orbital swath can&apos;t be widened the way the LOLA elevation window can, so it
                only covers a fraction of this crater. In the 3D view it&apos;s shown as a correctly-scaled photo
                resting on the real terrain, over the real hazard classification — not stretched to imply full
                coverage.
              </div>
            )}
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
            <Canvas camera={{ position: [19, 14, 19], fov: 42 }}>
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
                textureHalfM={selectedCandidate.textureHalfM}
              />

              <OrbitControls
                enablePan={false}
                maxPolarAngle={Math.PI / 2 - 0.02}
                minDistance={8}
                maxDistance={44}
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
