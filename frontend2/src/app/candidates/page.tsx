"use client";

import { useState, useMemo } from "react";
import { CANDIDATES, CandidateId } from "@/data/prism";
import { useIsLightTheme } from "@/hooks/useIsLightTheme";
import Link from "next/link";

function PolarInteractiveMap({
  selectedId,
  onSelect,
}: {
  selectedId: CandidateId;
  onSelect: (id: CandidateId) => void;
}) {
  const isLight = useIsLightTheme();
  const size = 600;
  const cx = size / 2;

  // Convert lat/lon to simple polar projection
  const toXY = (lat: number, lon: number, radius: number) => {
    // Map -90 to center, -80 to edge.
    // -80 is 10 degrees from pole.
    const degFromPole = 90 + lat;
    const r = (degFromPole / 14) * radius;
    const theta = (lon * Math.PI) / 180;
    return {
      x: cx + r * Math.sin(theta),
      y: cx - r * Math.cos(theta),
    };
  };

  const mapRadius = size * 0.44;

  return (
    <div style={{ position: "relative", width: "100%", maxWidth: `${size}px`, aspectRatio: "1/1", margin: "0 auto" }}>
      <svg width="100%" height="100%" viewBox={`0 0 ${size} ${size}`}>
        {/* Background Image of South Pole */}
        <image
          href="/south_pole_image.jpg"
          x={cx - mapRadius * 1.1}
          y={cx - mapRadius * 1.1}
          width={mapRadius * 2.2}
          height={mapRadius * 2.2}
          opacity={isLight ? 0.55 : 0.4}
          style={{ mixBlendMode: isLight ? "multiply" : "lighten", objectFit: "cover" }}
          preserveAspectRatio="xMidYMid slice"
        />
        {/* Grid rings */}
        {[1, 2, 3, 4].map((i) => (
          <circle
            key={i}
            cx={cx}
            cy={cx}
            r={(i / 4.5) * mapRadius}
            fill="none"
            stroke="var(--border)"
            strokeWidth="1"
          />
        ))}
        {/* Grid spokes */}
        {Array.from({ length: 8 }, (_, i) => {
          const angle = (i / 8) * Math.PI * 2;
          return (
            <line
              key={i}
              x1={cx}
              y1={cx}
              x2={cx + Math.sin(angle) * mapRadius}
              y2={cx - Math.cos(angle) * mapRadius}
              stroke="var(--border)"
              strokeWidth="1"
            />
          );
        })}
        {/* South Pole label */}
        <text x={cx} y={cx + 6} textAnchor="middle" fontSize="12" fill="var(--text-muted)" fontFamily="monospace">90°S</text>

        {/* Candidate dots */}
        {CANDIDATES.map((c) => {
          const pos = toXY(c.lat, c.lon, mapRadius);
          const isSelected = selectedId === c.id;
          const isPrimary = c.isPrimary;

          return (
            <g
              key={c.id}
              onClick={() => onSelect(c.id as CandidateId)}
              style={{ cursor: "pointer", transition: "all 0.3s ease" }}
            >
              {isSelected && (
                <circle cx={pos.x} cy={pos.y} r={24} fill="rgba(255,255,255,0.05)" stroke="rgba(255,255,255,0.15)" strokeWidth="1" />
              )}
              {isPrimary && (
                <circle cx={pos.x} cy={pos.y} r={16} fill="rgba(196,162,104,0.1)" stroke="rgba(196,162,104,0.4)" strokeWidth="1" />
              )}
              <circle
                cx={pos.x}
                cy={pos.y}
                r={isSelected ? 6 : isPrimary ? 5 : 4}
                fill={isSelected ? "#FFF" : isPrimary ? "#C4A268" : "rgba(62,107,154,0.8)"}
                stroke={isPrimary ? "#E4D89A" : "rgba(90,140,190,0.5)"}
                strokeWidth={isPrimary ? 1.5 : 1}
                style={{ transition: "all 0.3s ease" }}
              />
              {/* Labels for selected or primary */}
              {(isSelected || isPrimary) && (
                <text
                  x={pos.x + 12}
                  y={pos.y - 8}
                  fontSize="12"
                  fill={isSelected ? "#FFF" : "var(--amber)"}
                  fontFamily="monospace"
                  fontWeight="700"
                  style={{ pointerEvents: "none" }}
                >
                  {c.label}
                </text>
              )}
            </g>
          );
        })}
      </svg>

      {/* Decorative corners */}
      <div style={{ position: "absolute", top: 0, left: 0, padding: "20px", fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", letterSpacing: "0.14em" }}>
        LUNAR SOUTH POLE<br/>
        STEREOGRAPHIC PROJECTION
      </div>
      <div style={{ position: "absolute", bottom: 0, right: 0, padding: "20px", fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", letterSpacing: "0.14em", textAlign: "right" }}>
        7 PSR CANDIDATES<br/>
        PRISM MISSION DB
      </div>
    </div>
  );
}

export default function CandidatesPage() {
  const [selectedId, setSelectedId] = useState<CandidateId>("SP_840980_0797630");

  const selectedCandidate = useMemo(() => {
    return CANDIDATES.find((c) => c.id === selectedId) || CANDIDATES[0];
  }, [selectedId]);

  return (
    <main style={{ paddingTop: "var(--nav-h)", background: "var(--void)" }}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 500px", alignItems: "start", borderTop: "1px solid var(--border)" }}>

        {/* Left: Map Viewer */}
        <section style={{ position: "sticky", top: "var(--nav-h)", height: "calc(100dvh - var(--nav-h))", borderRight: "1px solid var(--border)", display: "flex", alignItems: "center", justifyContent: "center", padding: "40px" }}>
          <div style={{ position: "absolute", inset: 0, background: "radial-gradient(circle at center, rgba(62,107,154,0.05) 0%, transparent 60%)" }} />
          <PolarInteractiveMap selectedId={selectedId} onSelect={setSelectedId} />
        </section>

        {/* Right: Candidate Detail Panel */}
        <section style={{ background: "var(--surface)", display: "flex", flexDirection: "column" }}>

          {/* Header */}
          <div style={{ padding: "40px", borderBottom: "1px solid var(--border)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
              <div>
                <div className="label-caps" style={{ marginBottom: "8px" }}>Selected Target</div>
                <h1 style={{ fontFamily: "var(--font-mono)", fontSize: "28px", color: "var(--text-primary)", letterSpacing: "0.02em", margin: 0 }}>
                  {selectedCandidate.label}
                </h1>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "6px", alignItems: "flex-end" }}>
                {selectedCandidate.isPrimary && <span className="status-pill">Primary Target</span>}
                <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", letterSpacing: "0.1em", textTransform: "uppercase", color: "var(--text-secondary)", border: "1px solid var(--border)", padding: "2px 8px", borderRadius: "99px" }}>
                  Rank {selectedCandidate.rank}
                </span>
              </div>
            </div>

            <p style={{ fontFamily: "var(--font-body)", fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.6, margin: 0 }}>
              {selectedCandidate.shortDescription}
            </p>
          </div>

          {/* Location Data */}
          <div style={{ padding: "32px 40px", borderBottom: "1px solid var(--border)" }}>
            <div className="label-caps" style={{ marginBottom: "20px" }}>Coordinate Data</div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
              <div>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "4px" }}>Latitude</div>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: "16px", color: "var(--text-primary)" }}>{selectedCandidate.lat.toFixed(3)}° S</div>
              </div>
              <div>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "4px" }}>Longitude</div>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: "16px", color: "var(--text-primary)" }}>{selectedCandidate.lon.toFixed(3)}° E</div>
              </div>
              <div style={{ gridColumn: "1 / -1" }}>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "4px" }}>PSR Area</div>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: "16px", color: "var(--text-primary)" }}>{selectedCandidate.areaKm2.toFixed(3)} km²</div>
              </div>
            </div>
          </div>

          {/* Physics Evidence Score */}
          <div style={{ padding: "32px 40px", borderBottom: "1px solid var(--border)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: "20px" }}>
              <div className="label-caps">Physics Evidence Score</div>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "24px", color: selectedCandidate.isPrimary ? "var(--amber)" : "var(--text-primary)", lineHeight: 1 }}>
                {selectedCandidate.physicsScore.toFixed(3)}
              </div>
            </div>
            
            {/* Metric Deltas */}
            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              {[
                { label: "Δ Pv", val: selectedCandidate.deltaPv },
                { label: "Δ CPR", val: selectedCandidate.deltaCpr },
                { label: "Δ T-Ratio", val: selectedCandidate.deltaTratio },
                { label: "Δ SERD", val: selectedCandidate.deltaSerd },
              ].map((m) => (
                <div key={m.label} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: "var(--text-secondary)" }}>{m.label}</span>
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: m.val > 0 ? "var(--signal-high)" : m.val < 0 ? "var(--signal-warn)" : "var(--text-muted)" }}>
                    {m.val > 0 ? "+" : ""}{m.val.toFixed(4)}
                  </span>
                </div>
              ))}
            </div>
            <div style={{ fontFamily: "var(--font-mono)", fontSize: "9px", color: "var(--text-muted)", letterSpacing: "0.08em", marginTop: "16px", lineHeight: 1.5 }}>
              * Delta values represent (PSR Interior Mean - Surroundings Baseline Mean).
              Positive indicates anomalous signature vs local terrain.
            </div>
          </div>

          {/* Quick Imagery */}
          <div style={{ padding: "32px 40px" }}>
            <div className="label-caps" style={{ marginBottom: "16px" }}>Candidate Imagery Context</div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              <div>
                <img src={selectedCandidate.shadowcamImage} alt="ShadowCam" className="scientific-image" style={{ aspectRatio: "1/1", objectFit: "cover" }} />
                <div style={{ marginTop: "8px", fontFamily: "var(--font-mono)", fontSize: "9px", color: "var(--text-muted)", letterSpacing: "0.1em", textTransform: "uppercase" }}>ShadowCam Context</div>
              </div>
              <div>
                <img
                  src={selectedCandidate.hazardImage}
                  alt="Hazard Map"
                  className="scientific-image"
                  style={{
                    aspectRatio: selectedCandidate.isPrimary ? "1/1" : "4/1",
                    objectFit: selectedCandidate.isPrimary ? "cover" : "contain",
                    background: "#000",
                  }}
                />
                <div style={{ marginTop: "8px", fontFamily: "var(--font-mono)", fontSize: "9px", color: "var(--text-muted)", letterSpacing: "0.1em", textTransform: "uppercase" }}>LOLA Hazard Map</div>
              </div>
            </div>
            
            <div style={{ marginTop: "32px", display: "flex", gap: "12px" }}>
              <Link href={`/evidence?candidate=${selectedCandidate.id}`} style={{ flex: 1 }}>
                <button className="btn-ghost" style={{ width: "100%", justifyContent: "center" }}>Analyze Evidence</button>
              </Link>
              <Link href="/terrain" style={{ flex: 1 }}>
                <button className={selectedCandidate.isPrimary ? "btn-blue" : "btn-ghost"} style={{ width: "100%", justifyContent: "center" }}>View Terrain</button>
              </Link>
            </div>
          </div>

        </section>
      </div>

      <style>{`
        @media (max-width: 1024px) {
          main > div {
            grid-template-columns: 1fr !important;
            grid-template-rows: auto 1fr;
          }
          section:nth-child(1) {
            position: static !important;
            height: auto !important;
          }
          section:nth-child(2) {
            height: auto !important;
            border-left: none !important;
          }
        }
      `}</style>
    </main>
  );
}
