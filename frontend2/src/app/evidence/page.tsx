"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import { PRIMARY, CANDIDATES, FAUSTINI, CABEUS, spIdLabel } from "@/data/prism";

// Real per-candidate delta magnitudes across the shortlist run roughly ±0.15
// at most — used only to give the bar a sensible fill scale, not a claimed
// statistical bound.
const DELTA_BAR_SCALE = 0.15;

// Individual single-panel crops (PRISM/src/split_hazard_terrain_panels.py,
// split_radar_panels.py) -- real data, re-derived from the same LDEM/DFSAR
// reads already used for each site's composite figure, one file per metric
// instead of one multi-panel strip. Present for all 9 sites.
const panelImg = (id: string, metric: "pv" | "cpr" | "serd" | "tratio" | "slope" | "roughness" | "illum" | "tri") =>
  `/assets/prism/panels/${id}_${metric}_only.png`;

// ── Unified site adapter ─────────────────────────────────────────
// One consistent shape for all 9 sites so the page below never has to branch
// into a separate component tree per site. Faustini/Cabeus keep their own
// richer objects (FAUSTINI.subcraters, CABEUS.targeted, etc.) for the
// validation-detail section further down — this adapter only normalizes the
// fields every site can show in the same header/gallery/metrics layout.
type EvidenceSite = {
  id: string;
  dropdownLabel: string;
  name: string;
  isPrimary: boolean;
  isFeatured: boolean;
  areaKm2: number;
  radarImage: string;
  hazardImage: string;
  shadowcamImage: string;
  deltaPv: number;
  deltaCpr: number;
  deltaTratio: number;
  deltaSerd: number;
  mlPixel?: { meanInside: number; meanOutside: number; separation: number };
  shortDescription: string;
  externalEvidence?: string;
};

const EVIDENCE_SITES: EvidenceSite[] = [
  {
    id: FAUSTINI.id, dropdownLabel: `${spIdLabel(FAUSTINI.id)} Faustini`, name: "Faustini",
    isPrimary: false, isFeatured: true, areaKm2: FAUSTINI.areaKm2,
    radarImage: FAUSTINI.radarImage, hazardImage: FAUSTINI.hazardImage, shadowcamImage: FAUSTINI.shadowcamImage,
    deltaPv: FAUSTINI.wholePsr.pv.delta, deltaCpr: FAUSTINI.wholePsr.cpr.delta,
    deltaTratio: FAUSTINI.wholePsr.trt.delta, deltaSerd: FAUSTINI.wholePsr.srd.delta,
    shortDescription: "Externally-confirmed ice evidence (Sinha et al. 2026). Featured here as a validation case, not one of PRISM's 7 screened candidates.",
    externalEvidence: "M3 (Chandrayaan-1) spectral ice-absorption detection — Li et al. 2018, PNAS",
  },
  {
    id: CABEUS.id, dropdownLabel: `${spIdLabel(CABEUS.id)} Cabeus`, name: "Cabeus",
    isPrimary: false, isFeatured: true, areaKm2: CABEUS.areaKm2,
    radarImage: CABEUS.radarImage, hazardImage: CABEUS.hazardImage, shadowcamImage: CABEUS.shadowcamImage,
    deltaPv: CABEUS.wholePsr.pv.delta, deltaCpr: CABEUS.wholePsr.cpr.delta,
    deltaTratio: CABEUS.wholePsr.trt.delta, deltaSerd: CABEUS.wholePsr.srd.delta,
    shortDescription: "LCROSS direct impact-plume water detection. Featured here as a validation case, not one of PRISM's 7 screened candidates.",
    externalEvidence: CABEUS.externalEvidence,
  },
  ...CANDIDATES.map((c): EvidenceSite => ({
    id: c.id, dropdownLabel: c.isPrimary ? `${c.label} (Primary)` : c.label, name: c.label,
    isPrimary: c.isPrimary, isFeatured: false, areaKm2: c.areaKm2,
    radarImage: c.isPrimary ? PRIMARY.images.radar : c.radarImage,
    hazardImage: c.isPrimary ? PRIMARY.images.hazard : c.hazardImage,
    shadowcamImage: c.isPrimary ? PRIMARY.images.shadowcam : (c.shadowcamImage as string),
    deltaPv: c.deltaPv, deltaCpr: c.deltaCpr, deltaTratio: c.deltaTratio, deltaSerd: c.deltaSerd,
    mlPixel: c.mlPixel,
    shortDescription: c.shortDescription,
  })),
];

function MetricPanel({ label, delta, detailImg }: { label: string; delta: number; detailImg: string }) {
  const isPositive = delta > 0;
  const barColor = isPositive ? "var(--signal-high)" : "var(--signal-flag)";
  const fill = Math.min(Math.abs(delta) / DELTA_BAR_SCALE, 1) * 100;

  return (
    <div style={{ padding: "24px", background: "rgba(255,255,255,0.01)", border: "1px solid var(--border)", borderRadius: "4px" }}>
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

      <img src={detailImg} alt={label} className="scientific-image" style={{ width: "100%", aspectRatio: "1/1", objectFit: "cover" }} />
    </div>
  );
}

function DeltaRow({ label, delta }: { label: string; delta: number }) {
  const isPositive = delta > 0;
  const color = isPositive ? "var(--signal-high)" : "var(--signal-flag)";
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: "1px solid var(--border)" }}>
      <span style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: "var(--text-secondary)" }}>{label}</span>
      <span style={{ fontFamily: "var(--font-mono)", fontSize: "14px", color }}>
        {isPositive ? "+" : ""}{delta.toFixed(4)}
      </span>
    </div>
  );
}

function SubcraterCard({ sc }: { sc: (typeof FAUSTINI.subcraters)[number] }) {
  return (
    <div style={{ border: "1px solid var(--border)", borderRadius: "4px", overflow: "hidden" }}>
      <img src={sc.image} alt={`Faustini ${sc.id}`} className="scientific-image" style={{ width: "100%", aspectRatio: "3/1", objectFit: "contain", background: "#000" }} />
      <div style={{ padding: "16px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: "8px" }}>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "14px", color: "var(--amber)" }}>{sc.id}</span>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)" }}>{sc.diameterM}m feature</span>
        </div>
        <DeltaRow label="Δ Pv" delta={sc.pv.delta} />
        <DeltaRow label="Δ CPR" delta={sc.cpr.delta} />
        <DeltaRow label="Δ T-Ratio" delta={sc.trt.delta} />
        <DeltaRow label="Δ SERD" delta={sc.srd.delta} />
      </div>
    </div>
  );
}

// Extra, real detail specific to the two externally-validated sites —
// appended below the standard layout every site shares, not a separate page.
// This is also where the "why do Faustini/Cabeus look different" question
// gets answered directly, with real numbers, instead of asserting a radar
// finding this pipeline didn't actually make.
function ValidationDetail({ site }: { site: EvidenceSite }) {
  if (site.id === FAUSTINI.id) {
    return (
      <div style={{ marginTop: "56px", paddingTop: "40px", borderTop: "1px solid var(--border)" }}>
        <div className="label-caps" style={{ marginBottom: "16px" }}>Why The Whole-PSR Numbers Above Look Negative</div>
        <p style={{ fontFamily: "var(--font-body)", fontSize: "13px", color: "var(--text-secondary)", maxWidth: "760px", lineHeight: 1.7, marginBottom: "24px" }}>
          Faustini&apos;s published ice evidence (Sinha et al. 2026) is real, but localized to two small
          sub-craters, F2 and F3 — together a tiny fraction of Faustini&apos;s full {FAUSTINI.areaKm2.toFixed(1)} km²
          PSR. Averaging our radar metrics across the <em>entire</em> crater (the deltas above) dilutes that
          localized signal into the noise of a mostly-ordinary floor, which is exactly why they come out
          negative — that is the correct, expected result of applying a whole-PSR method to a site whose real
          signal is small and off-center, not an error. Re-running the identical method at F2/F3&apos;s exact
          coordinates below recovers a strongly anomalous signal, 2–5× larger than PRISM&apos;s own #1-ranked
          candidate — confirming the method works, once pointed at the right scale.
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
          {FAUSTINI.subcraters.map((sc) => <SubcraterCard key={sc.id} sc={sc} />)}
        </div>
      </div>
    );
  }

  if (site.id === CABEUS.id) {
    const t = CABEUS.targeted;
    return (
      <div style={{ marginTop: "56px", paddingTop: "40px", borderTop: "1px solid var(--border)" }}>
        <div className="label-caps" style={{ marginBottom: "16px" }}>Why The Whole-PSR Numbers Above Look Negative</div>
        <p style={{ fontFamily: "var(--font-body)", fontSize: "13px", color: "var(--text-secondary)", maxWidth: "760px", lineHeight: 1.7, marginBottom: "24px" }}>
          Cabeus&apos;s real claim to fame isn&apos;t a radar signature — it&apos;s LCROSS physically impacting the
          floor in 2009 and detecting water vapor directly in the ejecta plume, no remote inference involved.
          Re-running PRISM&apos;s own DFSAR method here, both across the whole PSR and targeted at the exact
          LCROSS coordinate below, does <em>not</em> show an anomalous reading either way — reported honestly,
          not asserted. That is a real, negative result for this specific radar method at this specific site;
          it doesn&apos;t contradict LCROSS&apos;s direct ground-truth detection, it just means DFSAR backscatter
          isn&apos;t the signal that would have found Cabeus&apos;s ice on its own.
        </p>
        <div className="label-caps" style={{ marginBottom: "16px" }}>{t.label}</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "40px" }}>
          <img src={t.image} alt="Cabeus LCROSS impact point" className="scientific-image" style={{ width: "100%", aspectRatio: "3/1", objectFit: "contain", background: "#000" }} />
          <div style={{ border: "1px solid var(--border)", borderRadius: "4px", padding: "16px" }}>
            <DeltaRow label="Δ Pv" delta={t.pv.delta} />
            <DeltaRow label="Δ CPR" delta={t.cpr.delta} />
            <DeltaRow label="Δ T-Ratio" delta={t.trt.delta} />
            <DeltaRow label="Δ SERD" delta={t.srd.delta} />
          </div>
        </div>
        <p style={{ fontFamily: "var(--font-body)", fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.6, marginTop: "16px", maxWidth: "760px" }}>
          {t.note}
        </p>
      </div>
    );
  }

  return null;
}

function CandidateSelect({ selectedId, onChange }: { selectedId: string; onChange: (id: string) => void }) {
  return (
    <select
      value={selectedId}
      onChange={(e) => onChange(e.target.value)}
      style={{
        background: "transparent", border: "1px solid var(--border)", color: "var(--text-primary)",
        padding: "6px 10px", borderRadius: "4px", fontFamily: "var(--font-mono)", fontSize: "12px", cursor: "pointer",
      }}
    >
      {EVIDENCE_SITES.map((s) => (
        <option key={s.id} value={s.id} style={{ background: "var(--surface)" }}>
          {s.dropdownLabel}
        </option>
      ))}
    </select>
  );
}

// Small real-image thumbnail used in the context grid below the radar hero.
function ContextThumb({ src, label }: { src: string; label: string }) {
  return (
    <div style={{ position: "relative", borderRadius: "4px", overflow: "hidden", border: "1px solid var(--border)" }}>
      <img src={src} alt={label} className="scientific-image" style={{ width: "100%", aspectRatio: "1/1", objectFit: "cover", display: "block" }} />
      <span
        style={{
          position: "absolute", bottom: "6px", left: "6px",
          fontFamily: "var(--font-mono)", fontSize: "8px", letterSpacing: "0.08em", textTransform: "uppercase",
          color: "#fff", background: "rgba(0,0,0,0.55)", padding: "2px 6px", borderRadius: "2px",
        }}
      >
        {label}
      </span>
    </div>
  );
}

function EvidenceContent() {
  const params = useSearchParams();
  const requested = params.get("candidate");
  const initialId = EVIDENCE_SITES.some((s) => s.id === requested) ? (requested as string) : PRIMARY.id;
  const [selectedId, setSelectedId] = useState<string>(initialId);

  const site = EVIDENCE_SITES.find((s) => s.id === selectedId) || EVIDENCE_SITES[0];
  const { isPrimary, isFeatured } = site;

  return (
    <main style={{ minHeight: "100dvh", paddingTop: "var(--nav-h)", background: "var(--void)" }}>
      <div className="container-page" style={{ padding: "40px 0" }}>

        {/* Header */}
        <div style={{ marginBottom: "40px", display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: "24px" }}>
          <div>
            <div className="label-caps" style={{ marginBottom: "16px" }}>
              {isFeatured ? "Featured Validation Site — Externally Confirmed Ice Evidence" : "02 — Analyze Evidence"}
            </div>
            <h1 style={{ fontFamily: "var(--font-display)", fontSize: "clamp(32px, 4vw, 48px)", fontWeight: 600, color: "var(--text-primary)", letterSpacing: "-0.02em", margin: "0 0 16px 0", lineHeight: 1.1 }}>
              {isFeatured ? `${site.name} Crater` : "Radar Signature Validation"}
            </h1>
            <p style={{ fontFamily: "var(--font-body)", fontSize: "14px", color: "var(--text-secondary)", maxWidth: "700px", lineHeight: 1.7 }}>
              {isFeatured ? (
                <>
                  {site.externalEvidence}. We ran PRISM&apos;s own real radar pipeline here too, using the same
                  data and methodology as every screened candidate on this page, as a validation check.
                </>
              ) : (
                <>
                  {site.name} shows {isPrimary ? "strong" : "measured"} anomalous backscatter across multiple
                  polarimetric parameters relative to local surroundings.
                  {isPrimary && ` Analysis conducted on Chandrayaan-2 DFSAR L-band data acquired ${PRIMARY.acquisition.date}.`}
                </>
              )}
            </p>
          </div>

          <div>
            <div className="label-caps" style={{ marginBottom: "8px" }}>Candidate</div>
            <CandidateSelect selectedId={selectedId} onChange={setSelectedId} />
          </div>
        </div>

        {/* 2-Column Layout */}
        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "40px", alignItems: "start" }}>

          {/* Left Col: Composite Image & Details */}
          <div>
            <div style={{ position: "relative", marginBottom: "16px" }}>
              <img
                src={site.radarImage}
                alt="Radar Composite"
                className="scientific-image"
                style={{ width: "100%" }}
              />
              <div style={{ position: "absolute", top: "16px", left: "16px", display: "flex", gap: "8px" }}>
                <span className="status-pill">DFSAR Radar Composite</span>
              </div>
            </div>

            {/* Same real-image context grid for every site: ShadowCam, hazard
                score, elevation/slope/roughness, illumination -- no site-
                specific special-casing, no locator/DOP-histogram exception. */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "10px", marginBottom: "24px" }}>
              <ContextThumb src={site.shadowcamImage} label="ShadowCam" />
              <ContextThumb src={site.hazardImage} label="Hazard Score" />
              <ContextThumb src={panelImg(site.id, "slope")} label="Slope" />
              <ContextThumb src={panelImg(site.id, "tri")} label="Roughness (TRI)" />
              <ContextThumb src={panelImg(site.id, "illum")} label="Illumination" />
              <ContextThumb src={`/assets/prism/elevation_only/${site.id}.png`} label="Elevation" />
            </div>

            {/* ML Box — real per-pixel Isolation Forest, where computed */}
            <div style={{ padding: "32px", border: "1px solid var(--border)", background: "rgba(255,255,255,0.01)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "24px", flexWrap: "wrap", gap: "16px" }}>
                <div>
                  <div className="label-caps" style={{ marginBottom: "8px" }}>Track J-v2 Machine Learning</div>
                  <h3 style={{ fontFamily: "var(--font-display)", fontSize: "20px", color: "var(--text-primary)", margin: 0 }}>Per-Pixel Isolation Forest — Ice Likelihood</h3>
                </div>
                {site.mlPixel && (
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontFamily: "var(--font-mono)", fontSize: "24px", color: site.mlPixel.separation > 0 ? "var(--signal-high)" : "var(--signal-flag)", lineHeight: 1 }}>
                      {site.mlPixel.separation > 0 ? "+" : ""}{site.mlPixel.separation.toFixed(4)}
                    </div>
                    <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", marginTop: "4px", textTransform: "uppercase" }}>
                      Interior − Surroundings Separation
                    </div>
                  </div>
                )}
              </div>
              {site.mlPixel ? (
                <>
                  <div style={{ display: "flex", gap: "32px", marginBottom: "16px" }}>
                    <div>
                      <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase" }}>Mean Inside PSR</div>
                      <div style={{ fontFamily: "var(--font-mono)", fontSize: "16px", color: "var(--text-primary)" }}>{site.mlPixel.meanInside.toFixed(4)}</div>
                    </div>
                    <div>
                      <div style={{ fontFamily: "var(--font-mono)", fontSize: "10px", color: "var(--text-muted)", textTransform: "uppercase" }}>Mean Outside (Approach)</div>
                      <div style={{ fontFamily: "var(--font-mono)", fontSize: "16px", color: "var(--text-primary)" }}>{site.mlPixel.meanOutside.toFixed(4)}</div>
                    </div>
                  </div>
                  <p style={{ fontFamily: "var(--font-body)", fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.6, margin: 0 }}>
                    Independent per-pixel Isolation Forest trained on real Pv/CPR/SERD/T-Ratio bands (not derived from the same
                    screening metric used to rank candidates). A positive separation means pixels inside the PSR score higher
                    on ice-likelihood than the surrounding approach terrain in the same window.
                  </p>
                </>
              ) : (
                <div style={{ padding: "12px", fontFamily: "var(--font-mono)", fontSize: "9px", color: "var(--text-muted)", textAlign: "center", border: "1px dashed var(--border)", borderRadius: "4px" }}>
                  Per-pixel Isolation Forest not run for this site
                </div>
              )}
            </div>
          </div>

          {/* Right Col: Metric Readouts — every site now gets its own real
              per-metric plot (PRISM/src/split_radar_panels.py), not just primary. */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", alignContent: "start" }}>
            <MetricPanel label="Pv (Volume Scatter)" delta={site.deltaPv} detailImg={panelImg(site.id, "pv")} />
            <MetricPanel label="CPR (Circular Pol. Ratio)" delta={site.deltaCpr} detailImg={panelImg(site.id, "cpr")} />
            <MetricPanel label="T-Ratio (Coherence)" delta={site.deltaTratio} detailImg={panelImg(site.id, "tratio")} />
            <MetricPanel label="SERD (Entropy Ratio)" delta={site.deltaSerd} detailImg={panelImg(site.id, "serd")} />
          </div>

        </div>

        <ValidationDetail site={site} />
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
