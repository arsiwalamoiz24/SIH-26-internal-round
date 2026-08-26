"use client";

import { useState } from "react";
import Link from "next/link";
import { TerrainVisualizer } from "@/components/visualizer/TerrainVisualizer";
import { GroundTruthValidationPanel } from "@/components/prism/GroundTruthValidationPanel";
import {
  getTargetCrater,
  getConfidenceBudget,
  getDrillSites,
  getVolumeEstimate,
  getRoverPaths,
  getPhysicsEvidenceScore,
  getMlAnomalyScore,
  getDopSummary,
  getPixelAnomalyScore,
  getPaperGroundTruthValidation,
} from "@/lib/api";
import 'material-symbols';

export default function IceDetection() {
  const [showBayesian, setShowBayesian] = useState(true);
  const [activePathId, setActivePathId] = useState<string>("path-discovery");
  const [assumedIcePct, setAssumedIcePct] = useState<number>(10.0);

  const target = getTargetCrater();
  const confidence = getConfidenceBudget();
  const drillSites = getDrillSites();
  const volume = getVolumeEstimate(assumedIcePct);
  const paths = getRoverPaths();
  const evidenceScore = getPhysicsEvidenceScore();
  const mlAnomaly = getMlAnomalyScore();
  const dop = getDopSummary();
  const pixelAnomaly = getPixelAnomalyScore();
  const groundTruth = getPaperGroundTruthValidation();

  const gaugeOffset = 282.7 * (1 - confidence.overall / 100);

  return (
    <main className="flex-1 p-grid-gutter flex gap-grid-gutter overflow-hidden bg-background h-[calc(100vh-80px)]">
      {/* Panel 1: Radar Evidence Surface & Likelihood View (50%) */}
      <section className="w-[50%] bento-card flex flex-col h-full overflow-hidden relative">
        <TerrainVisualizer showBayesian={showBayesian} activePathId={activePathId} />

        {/* Header Overlay */}
        <div className="absolute top-0 left-0 right-0 p-4 z-10 flex justify-between items-start pointer-events-none">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-h1 text-h2 text-on-surface m-0 drop-shadow-md">
                Radar Evidence &amp; Ice Likelihood
              </h2>
              <span className="bg-primary-fixed text-on-primary-fixed-variant tech-border border text-[9px] font-mono font-bold px-1.5 py-0.5 rounded shadow-sm">
                MODEL-DERIVED
              </span>
            </div>
            <div className="font-data-sm text-on-surface-variant uppercase tracking-wider drop-shadow-sm mt-1">
              CHANDRAYAAN-2 DFSAR L-BAND (2.5M/PX) • {target.psrId}
            </div>
          </div>

          {/* View Mode Toggle */}
          <div className="bg-surface/95 backdrop-blur-md tech-border rounded p-2 flex items-center gap-3 pointer-events-auto shadow-sm">
            <span className={`font-data-sm font-bold uppercase tracking-wide text-[11px] ${!showBayesian ? "text-primary font-black" : "text-on-surface-variant"}`}> 
              Binary CPR (&gt;1.0)
            </span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="sr-only peer"
                checked={showBayesian}
                onChange={() => setShowBayesian(!showBayesian)}
              />
              <div className="w-10 h-5 bg-outline-variant peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-[20px] peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-outline-variant after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary"></div>
            </label>
            <span
              className={`font-data-sm uppercase font-bold tracking-wide text-[11px] ${showBayesian ? "text-primary font-black" : "text-on-surface-variant"}`}
            >
              Probabilistic Likelihood
            </span>
          </div>
        </div>

        {/* Legend Overlay */}
        <div className="absolute bottom-4 mb-3 left-4 bg-surface/95 p-3.5 tech-border rounded shadow-sm z-10 backdrop-blur-md pointer-events-auto flex flex-col gap-3 max-w-[240px]">
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <span className="font-data-sm text-on-surface-variant uppercase tracking-wider font-semibold text-[10px]">
                {showBayesian ? "Ice Likelihood P(Ice)" : "Binary CPR (Literature Threshold)"}
              </span>
            </div>
            {showBayesian ? (
              <>
                <div className="flex h-3 w-full tech-border mb-1 rounded-[1px] overflow-hidden">
                  <div className="flex-1 bg-[#d1d5db]" title="0.0 - 0.2"></div>
                  <div className="flex-1 bg-[#93c5fd]" title="0.2 - 0.4"></div>
                  <div className="flex-1 bg-[#60a5fa]" title="0.4 - 0.6"></div>
                  <div className="flex-1 bg-[#3b82f6]" title="0.6 - 0.8"></div>
                  <div className="flex-1 bg-[#2563eb]" title="0.8 - 0.9"></div>
                  <div className="flex-1 bg-[#1d4ed8]" title="0.9 - 1.0"></div>
                </div>
                <div className="flex justify-between font-data-sm text-[9px] text-on-surface font-mono">
                  <span>0.0 (Regolith)</span>
                  <span>1.0 (Peak Anomaly)</span>
                </div>
              </>
            ) : (
              <div className="flex items-center gap-3 py-1 font-mono text-[10px]">
                <div className="flex items-center gap-1.5">
                  <span className="w-3 h-3 bg-[#1d4ed8] rounded-sm"></span> CPR &gt; 1.0 (7.3%)
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-3 h-3 bg-[#d1d5db] rounded-sm"></span> Normal
                </div>
              </div>
            )}
            <div className="text-[8px] text-outline font-mono mt-1">
              {showBayesian ? "Isolation Forest • Real Pv/CPR/SERD/T-Ratio pixels" : "Real DFSAR CPR Product"}
            </div>
          </div>

          <div className="tech-border-t pt-2.5">
            <div className="mb-1.5 font-data-sm text-on-surface-variant uppercase tracking-wider font-semibold text-[10px]">
              Pareto Trajectories (Derived)
            </div>
            <div className="flex flex-col gap-1.5">
              {paths.map((p) => (
                <div
                  key={p.id}
                  onClick={() => setActivePathId(p.id)}
                  className={`flex items-center justify-between p-1 rounded cursor-pointer transition-colors ${
                    activePathId === p.id ? "bg-surface-container-highest border border-primary/40" : "hover:bg-surface-container"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-[3px]" style={{ backgroundColor: p.color }}></div>
                    <span className={`font-data-sm text-[11px] ${activePathId === p.id ? "text-primary font-bold" : "text-on-surface"}`}>
                      {p.name.replace(" Trajectory", "")}
                    </span>
                  </div>
                  <span className="font-mono text-[10px] text-outline">{p.lengthKm} km</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Coordinate Readout */}
        <div className="absolute bottom-4 right-4 mb-3 bg-surface/95 p-3 tech-border rounded shadow-sm backdrop-blur-md min-w-[150px] z-10 pointer-events-auto font-mono text-[12px]">
          <div className="flex justify-between items-center mb-1">
            <span className="font-data-sm uppercase text-on-surface-variant text-[10px]">TARGET LAT</span>
            <span className="text-on-surface font-semibold">{Math.abs(target.latitude)}° S</span>
          </div>
          <div className="flex justify-between items-center mb-1">
            <span className="font-data-sm uppercase text-on-surface-variant text-[10px]">TARGET LON</span>
            <span className="text-on-surface font-semibold">{target.longitude}° E</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="font-data-sm uppercase text-on-surface-variant text-[10px]">CRATER AREA</span>
            <span className="text-primary font-semibold">{target.areaKm2} km²</span>
          </div>
        </div>
      </section>

      {/* Panel 2: Scientific Core (25%) */}
      <section className="w-[25%] flex flex-col mb-3 gap-grid-gutter h-full min-h-0 overflow-y-auto">
        {/* Science Confidence */}
        <div className="bento-card mx-1 flex flex-col shrink-0">
          <div className="bento-header">
            <h2 className="font-h2 text-h2 text-on-surface m-0 text-[14px]">Science Confidence</h2>
            <span className="text-[9px] font-mono text-outline font-bold uppercase">SNR DERIVED</span>
          </div>
          <div className="p-4 flex flex-col gap-4 items-center">
            <div className="relative w-28 h-28 flex items-center justify-center">
              <svg
                className="absolute inset-0 w-full h-full transform -rotate-90"
                viewBox="0 0 100 100"
              >
                <circle cx="50" cy="50" fill="none" r="45" stroke="#e5e7eb" strokeWidth="8"></circle>
                <circle
                  cx="50"
                  cy="50"
                  fill="none"
                  r="45"
                  stroke="#003f87"
                  strokeDasharray="282.7"
                  strokeDashoffset={gaugeOffset}
                  strokeLinecap="round"
                  strokeWidth="8"
                ></circle>
              </svg>
              <div className="text-center flex flex-col z-10">
                <span className="font-data-lg text-primary text-[28px] leading-none mono-nums font-bold">
                  {confidence.overall}
                  <span className="text-[16px]">%</span>
                </span>
              </div>
            </div>
            <span className="font-data-sm text-on-surface-variant uppercase tracking-wider font-semibold text-[10px]">
              QUANTITATIVE CONFIDENCE
            </span>

            <div className="grid grid-cols-1 w-full gap-2 tech-border-t pt-3">
              <div className="flex justify-between items-center p-2 bg-surface-container-low rounded border border-outline-variant text-[11px]">
                <span className="font-data-sm text-on-surface-variant">Radar Corroboration</span>
                <span className="font-data-sm text-[#10b981] font-bold uppercase">
                  {confidence.factors.radarAgreement} (+ΔPv, +ΔCPR)
                </span>
              </div>
              <div className="flex justify-between items-center p-2 bg-surface-container-low rounded border border-outline-variant text-[11px]">
                <span className="font-data-sm text-on-surface-variant">Anomaly SNR (Z-score)</span>
                <span className="font-data-sm text-primary font-bold mono-nums">
                  {confidence.factors.anomalySignificanceZ}σ
                </span>
              </div>
              <div className="flex justify-between items-center p-2 bg-surface-container-low rounded border border-outline-variant text-[11px]">
                <span className="font-data-sm text-on-surface-variant">Volume Anomaly ΔPv</span>
                <span className="font-data-sm text-on-surface mono-nums font-bold">
                  +{target.pvAnomaly} (0.51 vs 0.43)
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Physics Evidence Score / DOP / ML Anomaly */}
        <div className="bento-card mx-1 flex flex-col overflow-hidden shrink-0">
          <div className="bento-header shrink-0">
            <h3 className="font-data-md text-data-md text-on-surface m-0 uppercase text-[11px] tracking-wider">
              Multi-Track Evidence (Module 1)
            </h3>
            <span className="text-[9px] font-mono text-tertiary bg-surface-container px-1.5 py-0.5 rounded border tech-border uppercase font-bold">
              REAL PIPELINE
            </span>
          </div>
          <div className="p-3 flex flex-col gap-2 font-mono text-[11px]">
            <div className="flex justify-between items-center p-2 bg-surface-container-low rounded border border-outline-variant">
              <span className="text-on-surface-variant">Physics Evidence Score</span>
              <span className="text-primary font-bold">
                {evidenceScore.score.toFixed(2)} <span className="text-outline font-normal">(rank {evidenceScore.rank}/{evidenceScore.rankOf})</span>
              </span>
            </div>
            <div className="flex justify-between items-center p-2 bg-surface-container-low rounded border border-outline-variant">
              <span className="text-on-surface-variant">
                Candidate DOP (linear-pol)
                <span className="text-outline"> · not validated vs published</span>
              </span>
              <span className="text-on-surface font-semibold">
                {dop.linearPolDopMean.toFixed(3)} <span className="text-outline font-normal">(n={dop.nValidPx.toLocaleString()} px)</span>
              </span>
            </div>
            <div className="flex justify-between items-center p-2 bg-surface-container-low rounded border border-outline-variant">
              <span className="text-on-surface-variant">Isolation Forest Anomaly Rank (PSR-level)</span>
              <span className="text-on-surface font-semibold">{mlAnomaly.anomalyRank} of {mlAnomaly.anomalyRankOf}</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-surface-container-low rounded border border-outline-variant">
              <span className="text-on-surface-variant">Isolation Forest, per-pixel (n={pixelAnomaly.nPixelsValid.toLocaleString()})</span>
              <span className="text-on-surface font-semibold">
                {pixelAnomaly.meanIceLikelihoodInsidePsr.toFixed(3)} <span className="text-outline font-normal">vs {pixelAnomaly.meanIceLikelihoodOutsidePsr.toFixed(3)} outside</span>
              </span>
            </div>
            <p className="text-[9px] text-outline leading-relaxed mt-1">
              Evidence score is a <strong>ranking within our own 7-candidate shortlist</strong>, not an ice probability. PSR-level ML anomaly features are derived from the same Pv computation as the shortlist itself, so that rank is not independent. The per-pixel run above uses independent real Pv/CPR/SERD/T-Ratio bands per pixel &mdash; the PSR-interior vs. surroundings separation is real but modest, not a dramatic signal.
            </p>
          </div>
        </div>

        {/* External ground-truth validation vs the published literature */}
        <GroundTruthValidationPanel v={groundTruth} />

        {/* Depth-Resolved Profile */}
        <div className="bento-card mx-1 flex flex-col overflow-hidden shrink-0">
          <div className="bento-header shrink-0">
            <h3 className="font-data-md text-data-md text-on-surface m-0 uppercase text-[11px] tracking-wider">
              Radar Sounding / Depth Profile
            </h3>
            <span className="text-[9px] font-mono text-tertiary bg-surface-container px-1.5 py-0.5 rounded border tech-border uppercase font-bold">
              SINGLE-FREQ ACTIVE
            </span>
          </div>
          <div className="p-3 bg-surface-container-low/60 border-b border-outline-variant">
            <p className="text-[10px] font-mono text-on-surface-variant m-0 leading-relaxed">
              <strong>STATUS:</strong> Single-Frequency DFSAR L-Band (~1.5m skin depth) observation active. Dual-frequency S-Band co-registration pending.
            </p>
          </div>
          <div className="flex-1 p-3 relative min-h-[110px]">
            <div className="text-[10px] font-mono text-outline space-y-1.5">
              <div className="flex justify-between">
                <span>0.0m (Surface):</span> <span className="text-on-surface font-medium">Odd-bounce dominant (Regolith)</span>
              </div>
              <div className="flex justify-between">
                <span>0.5m - 1.5m:</span> <span className="text-primary font-semibold">Volume scattering peak (Pv=0.51)</span>
              </div>
              <div className="flex justify-between text-outline-variant">
                <span>&gt; 1.5m (Subsurface):</span> <span>L-band attenuation boundary</span>
              </div>
            </div>
          </div>
        </div>

        {/* Drill-Site Intelligence */}
        <div className="bento-card mx-1 mb-3 flex flex-col overflow-hidden shrink-0">
          <div className="bento-header">
            <h3 className="font-data-md text-data-md text-on-surface m-0 uppercase text-[11px] tracking-wider">
              Peak Radar Anomaly Coring Targets
            </h3>
            <span className="text-[9px] font-mono text-primary font-bold uppercase">REAL PEAKS</span>
          </div>
          <div className="p-3 flex flex-col gap-2">
            {drillSites.map((site, index) => (
              <div
                key={site.id}
                className={`p-2 rounded flex flex-col gap-1 transition-colors ${
                  index === 0
                    ? "border border-primary bg-surface-container"
                    : "tech-border bg-surface"
                }`}
              >
                <div className="flex justify-between items-center">
                  <span
                    className={`font-data-md text-[12px] ${index === 0 ? "text-primary font-bold" : "text-on-surface font-semibold"}`}
                  >
                    {site.name}
                  </span>
                  <span className="font-data-sm text-outline mono-nums text-[11px]">CONF: {site.confidence}%</span>
                </div>
                <span className="font-body-sm text-on-surface-variant text-[11px]">{site.rationale}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Panel 3: Mission Planning (25%) */}
      <section className="w-[25%] bento-card flex flex-col h-full min-h-0 overflow-hidden">
        <div className="bento-header shrink-0">
          <h2 className="font-h2 text-h2 text-on-surface m-0 text-[14px]">Mission Planning &amp; Yield</h2>
          <span className="material-symbols-outlined text-outline-variant text-[18px]">tune</span>
        </div>
        <div className="flex-1 p-4 flex flex-col gap-4 min-h-0 overflow-y-auto justify-between">
          <div className="flex flex-col gap-3 shrink-0">
            <div className="flex justify-between items-center">
              <h3 className="font-data-sm text-outline-variant uppercase tracking-wider text-[11px]">
                Pareto Objective Trade-off
              </h3>
              <span className="text-[9px] font-mono text-primary font-bold">GRAPH-SOLVER</span>
            </div>
            
            <div className="p-2.5 bg-surface-container-low tech-border rounded text-[11px] font-mono space-y-1.5">
              <div className="flex justify-between">
                <span className="text-on-surface-variant">Active Mode:</span>
                <span className="text-primary font-bold capitalize">{activePathId.replace("path-", "")}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-on-surface-variant">Path Distance:</span>
                <span className="text-on-surface font-semibold">{paths.find(p => p.id === activePathId)?.lengthKm} km</span>
              </div>
              <div className="flex justify-between">
                <span className="text-on-surface-variant">Traverse Cost Score:</span>
                <span className="text-on-surface font-semibold">{paths.find(p => p.id === activePathId)?.traverseCost}</span>
              </div>
            </div>
          </div>

          {/* Indicative Subsurface Volume Estimate */}
          <div className="p-3 bg-surface-container-low tech-border rounded flex flex-col gap-2 shrink-0">
            <div className="flex justify-between items-center">
              <span className="font-data-sm text-on-surface-variant uppercase font-semibold text-[10px]">
                Indicative Subsurface Volume Estimate
              </span>
              <span className="text-[8px] font-mono bg-primary/10 text-primary px-1 rounded font-bold">
                MODEL-DERIVED
              </span>
            </div>
            <div className="font-data-md text-on-background mono-nums font-bold text-[14px]">
              {(volume.mean / 1e6).toFixed(2)}M m³ <span className="text-[11px] text-outline">±{(volume.uncertainty / 1e6).toFixed(2)}M</span>
            </div>
            
            {/* Ice concentration slider with explicit assumption label */}
            <div className="mt-1">
              <div className="flex justify-between text-[10px] font-mono text-on-surface-variant mb-1">
                <span>Assumed Ice Conc (Slider):</span>
                <span className="text-primary font-bold">{assumedIcePct}% (Assumed)</span>
              </div>
              <input
                type="range"
                min="5"
                max="25"
                step="1"
                value={assumedIcePct}
                onChange={(e) => setAssumedIcePct(Number(e.target.value))}
                className="w-full h-1.5 bg-outline-variant rounded-lg appearance-none cursor-pointer accent-primary"
              />
              <div className="text-[8px] text-outline font-mono mt-1 leading-tight">
                Assumptions: Area {target.areaKm2}km² • High-Pv {target.highPvFraction*100}% • 1.5m L-band skin depth
              </div>
            </div>
          </div>

          <div className="bg-surface-container-low tech-border rounded p-3 shrink-0">
            <span className="font-data-sm text-on-surface-variant uppercase font-semibold mb-2 block text-[10px]">
              Methodology Comparison
            </span>
            <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
              <div className="p-2 tech-border rounded bg-surface">
                <div className="font-bold text-outline">Binary CPR (&gt;1)</div>
                <div className="text-[9px] text-on-surface-variant mt-1">
                  Pixel fraction: 7.33% (Discards scattering physics)
                </div>
              </div>
              <div className="p-2 tech-border rounded bg-primary/5 border-primary/40">
                <div className="font-bold text-primary">Probabilistic Model</div>
                <div className="text-[9px] text-primary mt-1">
                  Continuous likelihood: +0.081 anomaly isolated
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="p-3.5 tech-border-t bg-surface mb-3 shrink-0">
          <Link
            href="/simulation"
            className="w-full bg-primary text-on-primary py-2 rounded font-body-md text-[13px] font-bold hover:bg-primary-container transition-colors active:scale-95 flex items-center justify-center gap-2 shadow-sm"
          >
            <span className="material-symbols-outlined text-[18px]">rocket_launch</span>
            Execute Mission Simulation
          </Link>
        </div>
      </section>
    </main>
  );
}
