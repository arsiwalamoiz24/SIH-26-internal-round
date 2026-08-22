"use client";

import { useState } from "react";
import "material-symbols";
import { REAL_CANDIDATE } from "@/data/prismDemoData";
import { DemoDataBadge } from "@/components/prism/DemoDataBadge";
import { EvidenceScoreBadge } from "@/components/prism/EvidenceScoreBadge";
import { PhysicsEvidenceCard } from "@/components/prism/PhysicsEvidenceCard";
import { DopPanel } from "@/components/prism/DopPanel";
import { TerrainPanel } from "@/components/prism/TerrainPanel";
import { RadarVisualizationPanel } from "@/components/prism/RadarVisualizationPanel";
import { MlPanel } from "@/components/prism/MlPanel";
import { SouthPoleMap } from "@/components/prism/SouthPoleMap";
import { CandidateComparisonChart } from "@/components/prism/CandidateComparisonChart";
import { CandidateTimeSeriesChart } from "@/components/prism/CandidateTimeSeriesChart";

export default function PrismDashboard() {
  const c = REAL_CANDIDATE;
  const [showSynthetic, setShowSynthetic] = useState(false);

  return (
    <main className="flex-1 overflow-y-auto bg-background">
      <div className="px-grid-gutter pt-grid-gutter pb-8 flex flex-col gap-grid-gutter max-w-[1400px] mx-auto">
        {/* ── Candidate Overview ── */}
        <div className="bg-surface-container-lowest tech-border rounded p-4 flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="font-h1 text-h1 text-on-surface tracking-tight">{c.id}</span>
              <DemoDataBadge source={c.source} />
            </div>
            <div className="font-data-md text-data-md text-on-surface-variant mono-nums">
              Lat {c.latitude.toFixed(3)}° &nbsp;Lon {c.longitude.toFixed(3)}°
            </div>
          </div>
          <div className="flex flex-col items-start md:items-end gap-1 max-w-[520px]">
            <span className="bg-primary text-on-primary px-3 py-1 rounded font-body-sm font-semibold uppercase tracking-wider text-[12px]">
              {c.statusLabel}
            </span>
            <p className="font-body-sm text-[12px] text-on-surface-variant m-0 text-left md:text-right">
              {c.subtext}
            </p>
          </div>
        </div>

        {/* ── Evidence Score + Map ── */}
        <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-grid-gutter">
          <div className="flex flex-col gap-grid-gutter">
            <EvidenceScoreBadge evidence={c.evidenceScore} />
            <MlPanel ml={c.ml} />
          </div>
          <div className="h-[380px] overflow-hidden">
            <SouthPoleMap />
          </div>
        </div>

        {/* ── Physics Evidence Cards ── */}
        <div>
          <h2 className="font-h2 text-h2 text-on-surface uppercase tracking-tight mb-2">
            Physics Evidence
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-grid-gutter">
            <PhysicsEvidenceCard
              label="Pv"
              metric={c.pv}
              interpretation="Elevated volume-scattering fraction relative to the surrounding mosaic."
            />
            <PhysicsEvidenceCard
              label="CPR"
              metric={c.cpr}
              interpretation="High circular polarization ratio, consistent with a rough or volumetric scatterer."
            />
            <PhysicsEvidenceCard
              label="SERD"
              metric={c.serd}
              interpretation="Anomalously low relative to the mosaic — flagged for investigation."
              flagged
            />
            <PhysicsEvidenceCard
              label="T-Ratio"
              metric={c.tRatio}
              interpretation="High transmit-ratio signal, consistent with the other radar indicators."
            />
          </div>
        </div>

        {/* ── DOP + Terrain ── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-grid-gutter">
          <DopPanel dop={c.dop} dopImage={c.images.dop} histogramImage={c.images.dopHistogram} />
          <TerrainPanel terrain={c.terrain} terrainImage={c.images.terrain} />
        </div>

        {/* ── Radar Visualization ── */}
        <RadarVisualizationPanel candidate={c} />

        {/* ── Synthetic demo section (collapsible) ── */}
        <div className="bg-surface-container-lowest tech-border rounded p-4">
          <button
            onClick={() => setShowSynthetic((v) => !v)}
            className="w-full flex items-center justify-between font-h2 text-h2 text-on-surface uppercase tracking-tight"
          >
            <span className="flex items-center gap-2">
              Synthetic Demo Panels
              <DemoDataBadge source="synthetic_demo" />
            </span>
            <span className="material-symbols-outlined text-outline text-[20px]">
              {showSynthetic ? "expand_less" : "expand_more"}
            </span>
          </button>
          {showSynthetic && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-grid-gutter mt-4">
              <CandidateComparisonChart />
              <CandidateTimeSeriesChart />
            </div>
          )}
        </div>

        <div className="text-center font-body-sm text-[12px] text-on-surface-variant py-4">
          PRISM does not claim confirmed ice. It identifies and prioritizes scientifically
          interesting potential ice candidates for further validation.
        </div>
      </div>
    </main>
  );
}
