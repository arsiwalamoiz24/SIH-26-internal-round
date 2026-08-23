"use client";

import { useState } from "react";
import "material-symbols";
import { REAL_CANDIDATE } from "@/data/prismDemoData";
import { DemoDataBadge } from "@/components/prism/DemoDataBadge";
import { EvidenceScoreBadge } from "@/components/prism/EvidenceScoreBadge";
import { PhysicsEvidenceSystem } from "@/components/prism/PhysicsEvidenceSystem";
import { DopPanel } from "@/components/prism/DopPanel";
import { TerrainPanel } from "@/components/prism/TerrainPanel";
import { RadarVisualizationPanel } from "@/components/prism/RadarVisualizationPanel";
import { MlPanel } from "@/components/prism/MlPanel";
import { SouthPoleMap } from "@/components/prism/SouthPoleMap";
import { CandidateComparisonChart } from "@/components/prism/CandidateComparisonChart";
import { CandidateTimeSeriesChart } from "@/components/prism/CandidateTimeSeriesChart";

const PHYSICS_INDICATORS = (c: typeof REAL_CANDIDATE) => [
  { label: "Pv", metric: c.pv, interpretation: "Elevated volume-scattering fraction relative to the surrounding mosaic." },
  { label: "CPR", metric: c.cpr, interpretation: "High circular polarization ratio, consistent with a rough or volumetric scatterer." },
  { label: "SERD", metric: c.serd, interpretation: "Anomalously low relative to the mosaic — flagged for investigation.", flagged: true },
  { label: "T-Ratio", metric: c.tRatio, interpretation: "High transmit-ratio signal, consistent with the other radar indicators." },
];

export default function PrismDashboard() {
  const c = REAL_CANDIDATE;
  const [showSynthetic, setShowSynthetic] = useState(false);

  return (
    <main className="flex-1 overflow-y-auto bg-background">
      <div className="px-6 pt-5 pb-10 flex flex-col gap-8 max-w-[1400px] mx-auto">
        {/* ── Mission strip — candidate identity, borderless band ── */}
        <div className="instrument-band pb-4 flex flex-wrap items-end justify-between gap-4">
          <div className="flex flex-col gap-1">
            <div className="flex items-baseline gap-3">
              <span className="font-data-lg text-[26px] font-semibold text-on-surface tracking-tight mono-nums">
                {c.id}
              </span>
              <span className="font-data-md text-[13px] text-on-surface-variant mono-nums">
                {c.latitude.toFixed(3)}°, {c.longitude.toFixed(3)}°
              </span>
            </div>
            <p className="text-[12px] text-on-surface-variant m-0 max-w-[64ch]">{c.subtext}</p>
          </div>
          <div className="flex flex-col items-end gap-1.5">
            <span className="coord-label text-primary font-semibold">{c.statusLabel}</span>
            <DemoDataBadge source={c.source} />
          </div>
        </div>

        {/* ── Hero: map (dominant) + evidence stack ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          <div className="lg:col-span-8 h-[560px]">
            <SouthPoleMap />
          </div>
          <div className="lg:col-span-4 flex flex-col">
            <EvidenceScoreBadge evidence={c.evidenceScore} />
            <div className="border-t border-outline-variant my-4" />
            <MlPanel ml={c.ml} />
          </div>
        </div>

        {/* ── Physics Evidence — one unified analytical system ── */}
        <PhysicsEvidenceSystem indicators={PHYSICS_INDICATORS(c)} />

        {/* ── Radar (image-led, wide) + DOP (stat-led, narrow) ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch">
          <div className="lg:col-span-7">
            <RadarVisualizationPanel candidate={c} />
          </div>
          <div className="lg:col-span-5">
            <DopPanel dop={c.dop} dopImage={c.images.dop} histogramImage={c.images.dopHistogram} />
          </div>
        </div>

        {/* ── Terrain — asymmetric image/stat merge, mostly borderless ── */}
        <TerrainPanel terrain={c.terrain} terrainImage={c.images.terrain} />

        {/* ── Secondary diagnostics — muted, synthetic, collapsed ── */}
        <div className="border-t border-dashed border-outline-variant pt-4">
          <button
            onClick={() => setShowSynthetic((v) => !v)}
            className="w-full flex items-center justify-between text-left"
          >
            <span className="flex items-center gap-2 coord-label text-[11px]">
              Secondary Diagnostics
              <DemoDataBadge source="synthetic_demo" />
            </span>
            <span className="material-symbols-outlined text-outline text-[18px]">
              {showSynthetic ? "expand_less" : "expand_more"}
            </span>
          </button>
          {showSynthetic && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mt-4">
              <CandidateComparisonChart />
              <CandidateTimeSeriesChart />
            </div>
          )}
        </div>

        <div className="text-center text-[11px] text-on-surface-variant py-2">
          PRISM does not claim confirmed ice. It identifies and prioritizes scientifically
          interesting potential ice candidates for further validation.
        </div>
      </div>
    </main>
  );
}
