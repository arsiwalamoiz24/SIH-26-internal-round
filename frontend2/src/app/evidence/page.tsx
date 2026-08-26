"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import { PRIMARY, CANDIDATES, CandidateId } from "@/data/prism";

// Real per-candidate delta magnitudes across the shortlist run roughly ±0.15
// at most — used only to give the bar a sensible fill scale, not a claimed
// statistical bound.
const DELTA_BAR_SCALE = 0.15;

function MetricPanel({ label, delta, detailImg }: { label: string; delta: number; detailImg?: string }) {
  const isPositive = delta > 0;
  const barColor = isPositive ? "var(--signal-high)" : "var(--signal-flag)";
  const fill = Math.min(Math.abs(delta) / DELTA_BAR_SCALE, 1) * 100;

  return (
    <div className="metric-block" style={{ padding: "24px", background: "rgba(255,255,255,0.01)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
        <div style={{ fontFamily: "var(--font-mono)", fontSize: "14px", letterSpacing: "0.1em", textTransform: "uppercase", color: "var(--text-primary)" }}>
          {label}
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: "24px", color: "var(--text-primary)", lineHeight: 1 }}>
            {isPositive ? "+" : ""}{delta.toFixed(4)}
          </div>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: barColor, marginTop: "4px" }}>
            Δ VS SURROUNDINGS {!isPositive && "⚑"}
          </div>
        </div>
      </div>

      <div style={{ height: "4px", background: "var(--border)", borderRadius: "2px", overflow: "hidden", marginBottom: "20px" }}>
        <div style={{ height: "100%", width: `${Math.max(fill, 2)}%`, background: barColor, borderRadius: "2px", transition: "width 1s ease" }} />
      </div>

      {detailImg ? (
        <img src={detailImg} alt={label} className="scientific-image" style={{ width: "100%", height: "120px", objectFit: "cover" }} />
      ) : (
        <div style={{ padding: "12px", fontFamily: "var(--font-mono)", fontSize: "9px", color: "var(--text-muted)", textAlign: "center", border: "1px dashed var(--border)", borderRadius: "4px", lineHeight: 1.5 }}>
          Per-metric plot pending additional radar source data
        </div>
      )}
    </div>
  );
}

function EvidenceContent() {
  const params = useSearchParams();
  const requested = params.get("candidate");
  const validId = CANDIDATES.some((c) => c.id === requested) ? (requested as CandidateId) : PRIMARY.id as CandidateId;
  const [selectedId, setSelectedId] = useState<CandidateId>(validId);

  const candidate = CANDIDATES.find((c) => c.id === selectedId) || CANDIDATES[0];
  const isPrimary = candidate.isPrimary;

  return (
    <main style={{ minHeight: "100dvh", paddingTop: "var(--nav-h)", background: "var(--void)" }}>
      <div className="container-page" style={{ padding: "40px 0" }}>

        {/* Header */}
        <div style={{ marginBottom: "40px", display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: "24px" }}>
          <div>
            <div className="label-caps" style={{ marginBottom: "16px" }}>02 — Analyze Evidence</div>
            <h1 style={{ fontFamily: "var(--font-display)", fontSize: "clamp(32px, 4vw, 48px)", fontWeight: 600, color: "var(--text-primary)", letterSpacing: "-0.02em", margin: "0 0 16px 0", lineHeight: 1.1 }}>
              Radar Signature Validation
            </h1>
            <p style={{ fontFamily: "var(--font-body)", fontSize: "14px", color: "var(--text-secondary)", maxWidth: "600px", lineHeight: 1.6 }}>
              {candidate.label} shows {isPrimary ? "strong" : "measured"} anomalous backscatter across multiple
              polarimetric parameters relative to local surroundings.
              {isPrimary && ` Analysis conducted on Chandrayaan-2 DFSAR L-band data acquired ${PRIMARY.acquisition.date}.`}
            </p>
          </div>

          <div>
            <div className="label-caps" style={{ marginBottom: "8px" }}>Candidate</div>
            <select
              value={selectedId}
              onChange={(e) => setSelectedId(e.target.value as CandidateId)}
              style={{
                background: "transparent", border: "1px solid var(--border)", color: "var(--text-primary)",
                padding: "6px 10px", borderRadius: "4px", fontFamily: "var(--font-mono)", fontSize: "12px", cursor: "pointer",
              }}
            >
              {CANDIDATES.map((c) => (
                <option key={c.id} value={c.id} style={{ background: "var(--surface)" }}>
                  {c.label} {c.isPrimary ? "(Primary)" : ""}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* 2-Column Layout */}
        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "40px", alignItems: "start" }}>

          {/* Left Col: Composite Image & Details */}
          <div>
            <div style={{ position: "relative", marginBottom: "24px" }}>
              <img
                src={isPrimary ? PRIMARY.images.radar : candidate.hazardImage}
                alt={isPrimary ? "Radar Composite" : "Hazard Map"}
                className="scientific-image"
                style={{ width: "100%", aspectRatio: isPrimary ? undefined : "4/1", objectFit: isPrimary ? undefined : "contain", background: isPrimary ? undefined : "#000" }}
              />
              <div style={{ position: "absolute", top: "16px", left: "16px", display: "flex", gap: "8px" }}>
                <span className="status-pill">{isPrimary ? "False Color Composite" : "Hazard Map (real data)"}</span>
              </div>
            </div>

            {!isPrimary && (
              <div style={{ marginBottom: "24px", padding: "12px 16px", fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", border: "1px dashed var(--border)", borderRadius: "4px", lineHeight: 1.6 }}>
                Full radar false-color composite, DOP histogram, and locator imagery are available for the primary target only — raw DFSAR source data for this candidate is pending.
              </div>
            )}

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              {isPrimary ? (
                <>
                  <img src={PRIMARY.images.locator} alt="South Pole Locator" className="scientific-image" style={{ width: "100%", height: "200px", objectFit: "cover" }} />
                  <img src={PRIMARY.images.dopHistogram} alt="DOP Histogram" className="scientific-image" style={{ width: "100%", height: "200px", objectFit: "cover" }} />
                </>
              ) : (
                <>
                  <img src={candidate.shadowcamImage} alt="ShadowCam" className="scientific-image" style={{ width: "100%", height: "200px", objectFit: "cover" }} />
                  <img src={candidate.terrainImage} alt="Terrain Composite" className="scientific-image" style={{ width: "100%", height: "200px", objectFit: "cover" }} />
                </>
              )}
            </div>

            {/* ML Box — real per-pixel Isolation Forest, available for all 7 */}
            <div style={{ marginTop: "40px", padding: "32px", border: "1px solid var(--border)", background: "rgba(255,255,255,0.01)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "24px", flexWrap: "wrap", gap: "16px" }}>
                <div>
                  <div className="label-caps" style={{ marginBottom: "8px" }}>Track J-v2 Machine Learning</div>
                  <h3 style={{ fontFamily: "var(--font-display)", fontSize: "20px", color: "var(--text-primary)", margin: 0 }}>Per-Pixel Isolation Forest — Ice Likelihood</h3>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontFamily: "var(--font-mono)", fontSize: "24px", color: candidate.mlPixel.separation > 0 ? "var(--signal-high)" : "var(--signal-flag)", lineHeight: 1 }}>
                    {candidate.mlPixel.separation > 0 ? "+" : ""}{candidate.mlPixel.separation.toFixed(4)}
                  </div>
                  <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", marginTop: "4px", textTransform: "uppercase" }}>
                    Interior − Surroundings Separation
                  </div>
                </div>
              </div>
              <div style={{ display: "flex", gap: "32px", marginBottom: "16px" }}>
                <div>
                  <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase" }}>Mean Inside PSR</div>
                  <div style={{ fontFamily: "var(--font-mono)", fontSize: "16px", color: "var(--text-primary)" }}>{candidate.mlPixel.meanInside.toFixed(4)}</div>
                </div>
                <div>
                  <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase" }}>Mean Outside (Approach)</div>
                  <div style={{ fontFamily: "var(--font-mono)", fontSize: "16px", color: "var(--text-primary)" }}>{candidate.mlPixel.meanOutside.toFixed(4)}</div>
                </div>
              </div>
              <p style={{ fontFamily: "var(--font-body)", fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.6, margin: 0 }}>
                Independent per-pixel Isolation Forest trained on real Pv/CPR/SERD/T-Ratio bands (not derived from the same
                screening metric used to rank candidates). A positive separation means pixels inside the PSR score higher
                on ice-likelihood than the surrounding approach terrain in the same window.
              </p>
            </div>
          </div>

          {/* Right Col: Metric Readouts */}
          <div style={{ border: "1px solid var(--border)", borderRadius: "4px", overflow: "hidden" }}>
            <MetricPanel
              label="Pv (Volume Scatter)"
              delta={candidate.deltaPv}
              detailImg={isPrimary ? PRIMARY.images.pv : undefined}
            />
            <MetricPanel
              label="CPR (Circular Pol. Ratio)"
              delta={candidate.deltaCpr}
              detailImg={isPrimary ? PRIMARY.images.cpr : undefined}
            />
            <MetricPanel
              label="T-Ratio (Coherence)"
              delta={candidate.deltaTratio}
              detailImg={isPrimary ? PRIMARY.images.tratio : undefined}
            />
            <MetricPanel
              label="SERD (Entropy Ratio)"
              delta={candidate.deltaSerd}
              detailImg={isPrimary ? PRIMARY.images.serd : undefined}
            />
          </div>

        </div>
      </div>

      <style>{`
        @media (max-width: 900px) {
          main > .container-page > div:nth-child(2) {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </main>
  );
}

export default function EvidencePage() {
  return (
    <Suspense fallback={null}>
      <EvidenceContent />
    </Suspense>
  );
}
