"use client";

import { useState } from "react";
import pvFractionImage from "@/assets/pv-fraction-overview.png";
import candidateTiersImage from "@/assets/psr-candidate-tiers.png";
import topCandidateImage from "@/assets/top-candidate-detail.png";
import { getMissionOverview } from "@/lib/mission-data";
import "material-symbols";

type MapView = "combined" | "candidate";

const MAP_VIEWS: Record<
  MapView,
  { label: string; caption: string }
> = {
  combined: {
    label: "Pv / Tiers",
    caption: "Pv Fraction + PSR-gated candidate tiers",
  },
  candidate: {
    label: "Top Candidate",
    caption: "SP_840980_0797630 — Y4R RGB, Pv, and anomaly vs local surroundings",
  },
};

export default function MissionOverview() {
  const [mapView, setMapView] = useState<MapView>("combined");
  const data = getMissionOverview();
  const view = MAP_VIEWS[mapView];
  const gaugeRotate = -45 + 1.543 * data.dataset.psrCoveragePct;

  return (
    <main className="flex-1 px-grid-gutter pt-grid-gutter pb-8 flex gap-grid-gutter overflow-hidden bg-background">
      {/* ── LEFT: Radar Screening Map + Phase Cards ── */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">

        {/* Map Module */}
        <div className="bg-surface-container-lowest tech-border rounded flex-1 flex flex-col overflow-hidden relative shadow-sm min-h-0">
          {/* Module header */}
          <div className="flex justify-between items-center px-4 py-2 tech-border-b bg-surface shrink-0">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-outline text-[18px]">map</span>
              <span className="font-body-md font-semibold text-on-surface uppercase tracking-wider text-[13px]">
                South Pole DFSAR Screening
              </span>
            </div>
            {/* View toggle — combined (side-by-side) vs single Top Candidate */}
            <div className="flex gap-1 bg-surface-container-low rounded p-0.5">
              {(Object.keys(MAP_VIEWS) as MapView[]).map((key) => (
                <button
                  key={key}
                  onClick={() => setMapView(key)}
                  className={`px-2.5 py-1 rounded-sm font-data-sm text-[11px] uppercase tracking-wide transition-colors ${
                    mapView === key
                      ? "bg-primary text-on-primary font-semibold"
                      : "text-on-surface-variant hover:bg-surface-container-high"
                  }`}
                >
                  {MAP_VIEWS[key].label}
                </button>
              ))}
            </div>
          </div>

          {/* Map content */}
          <div className="flex-1 min-h-0 relative">
            {mapView === "combined" ? (
              <div className="absolute inset-0 flex gap-1 p-1">
                <div className="flex-1 min-w-0 relative overflow-hidden rounded-sm">
                  <img
                    src={pvFractionImage.src}
                    alt="Pv Fraction overview"
                    className="w-full h-full object-contain"
                  />
                  <div className="absolute bottom-1 left-1 bg-surface/80 backdrop-blur-sm px-2 py-0.5 rounded text-[10px] font-data-sm text-on-surface uppercase tracking-wide truncate">
                    Pv Fraction — Vol / Total
                  </div>
                </div>
                <div className="flex-1 min-w-0 relative overflow-hidden rounded-sm">
                  <img
                    src={candidateTiersImage.src}
                    alt="PSR candidate tiers"
                    className="w-full h-full object-contain"
                  />
                  <div className="absolute bottom-1 left-1 bg-surface/80 backdrop-blur-sm px-2 py-0.5 rounded text-[10px] font-data-sm text-on-surface uppercase tracking-wide truncate">
                    PSR Tiers — outside / low / moderate / high Pv
                  </div>
                </div>
              </div>
            ) : (
              <img
                src={topCandidateImage.src}
                alt="Top Candidate"
                className="w-full h-full object-contain"
              />
            )}
          </div>
        </div>

        <div className="grid grid-cols-4 gap-grid-gutter shrink-0 p-4" style={{ height: "130px" }}>
          <div className="bg-surface-container-lowest tech-border rounded p-3 flex flex-col justify-between">
            <div className="font-data-sm text-outline uppercase text-[10px] tracking-wider">Detect Phase</div>
            <div>
              <div className="text-data-lg font-data-lg text-primary font-semibold">DFSAR L4 Active</div>
              <div className="font-data-sm text-on-surface-variant text-[11px] mt-0.5">
                Grid: ~{data.dataset.gridResolutionM} m/px
              </div>
            </div>
          </div>

          <div className="bg-surface-container-lowest tech-border rounded p-3 flex flex-col justify-between">
            <div className="font-data-sm text-outline uppercase text-[10px] tracking-wider">Characterize</div>
            <div>
              <div className="text-data-lg font-data-lg text-primary font-semibold">
                {data.tierCounts.psrHighPv.toLocaleString()} px
              </div>
              <div className="font-data-sm text-on-surface-variant text-[11px] mt-0.5">PSR / high-Pv tier</div>
            </div>
          </div>

          <div className="bg-surface-container-lowest tech-border rounded p-3 flex flex-col justify-between">
            <div className="font-data-sm text-outline uppercase text-[10px] tracking-wider">Screen Phase</div>
            <div>
              <div className="text-data-lg font-data-lg text-primary font-semibold">
                {data.shortlist.length} Shortlisted
              </div>
              <div className="font-data-sm text-on-surface-variant text-[11px] mt-0.5">
                Multi-indicator PSR candidates
              </div>
            </div>
          </div>

          <div className="bg-surface-container-high/60 border border-dashed border-outline-variant rounded p-3 flex flex-col justify-between relative overflow-hidden">
            <div className="font-data-sm text-outline uppercase text-[10px] tracking-wider relative z-10">
              Land / Traverse
            </div>
            <div className="relative z-10">
              <div className="text-data-lg font-data-lg text-outline font-bold">Pending</div>
              <div className="font-data-sm text-outline text-[11px] mt-0.5">Needs slope + path model</div>
            </div>
            <span
              className="material-symbols-outlined absolute -bottom-4 -right-2 text-[80px] text-outline/10 select-none pointer-events-none"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              route
            </span>
          </div>
        </div>
      </div>

      {/* ── RIGHT SIDEBAR ── */}
      <div className="w-[320px] flex flex-col shrink-0 overflow-y-auto">
        <div className="bg-surface-container-lowest tech-border rounded p-4 shrink-0 m-2">
          <div className="flex items-center justify-between mb-4 pb-2 tech-border-b">
            <h2 className="font-h2 text-h2 text-on-surface uppercase tracking-tight m-0">Mission Status</h2>
            <span className="bg-surface-container-high text-primary px-2 py-0.5 rounded font-data-sm border border-outline-variant uppercase text-[11px]">
              Screening
            </span>
          </div>
          <div className="flex gap-4 justify-between">
            <div>
              <div className="font-data-sm text-outline uppercase text-[10px] tracking-wider mb-1">
                Top Candidate PSR
              </div>
              <div className="font-data-md text-data-md text-on-surface font-semibold">
                {data.topCandidate.psrId}
              </div>
            </div>
            <div>
              <div className="font-data-sm text-outline uppercase text-[10px] tracking-wider mb-1">
                Coordinates
              </div>
              <div className="font-data-md text-data-md text-on-surface mono-nums">
                {Math.abs(data.topCandidate.lat).toFixed(2)}°S, {data.topCandidate.lon.toFixed(2)}°E
              </div>
            </div>
          </div>
        </div>

        <div className="bg-surface-container-lowest tech-border rounded p-4 shrink-0 m-2">
          <h2 className="font-h2 text-h2 text-on-surface uppercase tracking-tight mb-4 flex items-center gap-2 m-0">
            <span
              className="material-symbols-outlined text-outline text-[16px]"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              analytics
            </span>
            Data Coverage Budget
          </h2>

          <div className="flex items-center justify-center mb-5">
            <div className="relative w-[120px] h-[60px] overflow-hidden">
              <div
                className="absolute w-[120px] h-[120px] rounded-full"
                style={{
                  border: "12px solid #e5eeff",
                  borderBottomColor: "transparent",
                  borderLeftColor: "transparent",
                  transform: "rotate(-45deg)",
                }}
              />
              <div
                className="absolute w-[120px] h-[120px] rounded-full transition-transform duration-1000"
                style={{
                  border: "12px solid #0056b3",
                  borderBottomColor: "transparent",
                  borderLeftColor: "transparent",
                  transform: `rotate(${gaugeRotate}deg)`,
                }}
              />
              <div className="absolute inset-0 flex flex-col items-center justify-end pb-1">
                <span className="font-h1 text-primary leading-none">
                  {data.dataset.psrCoveragePct.toFixed(0)}
                  <span className="text-h2">%</span>
                </span>
              </div>
            </div>
          </div>

          <div className="bg-surface-container-low rounded p-2 grid grid-cols-2 gap-2 text-center tech-border">
            <div className="border-r border-outline-variant pr-2">
              <div className="font-data-sm text-outline uppercase text-[10px] tracking-wider">
                PSR Catalog
              </div>
              <div className="font-data-md text-secondary font-semibold mt-0.5">
                {data.dataset.psrCatalogTotal} (LOLA)
              </div>
            </div>
            <div>
              <div className="font-data-sm text-outline uppercase text-[10px] tracking-wider">
                With Radar Data
              </div>
              <div className="font-data-md text-primary font-semibold mono-nums mt-0.5">
                {data.dataset.psrWithRadarCoverage}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-surface-container-lowest tech-border rounded p-4 flex flex-col m-2 mb-4">
          <h2 className="font-body-md font-semibold text-on-surface uppercase tracking-tight mb-4 pb-2 tech-border-b m-0">
            Objective Summaries
          </h2>
          <div className="flex flex-col gap-4 flex-1">
            <div className="flex gap-3 items-start">
              <div className="bg-surface-container-highest text-primary w-6 h-6 rounded flex items-center justify-center font-data-sm flex-shrink-0 mt-0.5 font-semibold text-[12px]">
                1
              </div>
              <div className="w-full">
                <div className="font-body-sm font-semibold text-on-surface uppercase mb-1 text-[11px] tracking-wider">
                  Ice Characterization
                </div>
                <div className="flex justify-between items-center font-data-md bg-surface p-1.5 tech-border rounded-sm text-[13px]">
                  <span className="text-on-surface-variant">Median Pv:</span>
                  <span className="mono-nums">
                    {data.pvFraction.median.toFixed(3)}{" "}
                    <span className="text-outline text-[11px]">
                      (p90 {data.pvFraction.p90.toFixed(3)})
                    </span>
                  </span>
                </div>
                <div className="flex justify-between items-center font-data-md px-1.5 mt-1 text-[13px]">
                  <span className="text-on-surface-variant font-data-sm text-[11px]">
                    Top candidate Pv:
                  </span>
                  <span className="text-primary font-bold mono-nums">
                    {data.topCandidate.pvMean.toFixed(3)}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex gap-3 items-start">
              <div className="bg-surface-container-highest text-primary w-6 h-6 rounded flex items-center justify-center font-data-sm flex-shrink-0 mt-0.5 font-semibold text-[12px]">
                2
              </div>
              <div className="w-full">
                <div className="font-body-sm font-semibold text-on-surface uppercase mb-1 text-[11px] tracking-wider">
                  Cross-Check (CPR / T-Ratio)
                </div>
                <div className="flex justify-between items-center font-data-md bg-surface p-1.5 tech-border rounded-sm text-[13px]">
                  <span className="text-on-surface-variant">CPR Δ vs surroundings:</span>
                  <span className="mono-nums">
                    +{data.topCandidate.cprDiffVsSurroundings.toFixed(3)}
                  </span>
                </div>
                <div className="flex justify-between items-center font-data-md px-1.5 mt-1 text-[13px]">
                  <span className="text-on-surface-variant font-data-sm text-[11px]">
                    Signal agreement:
                  </span>
                  <span className="text-secondary font-bold">
                    {data.topCandidate.agreeingSignals}/3 indicators
                  </span>
                </div>
              </div>
            </div>

            <div className="flex gap-3 items-start opacity-70">
              <div className="bg-surface-container-highest text-outline w-6 h-6 rounded flex items-center justify-center font-data-sm flex-shrink-0 mt-0.5 font-semibold text-[12px]">
                3
              </div>
              <div className="w-full">
                <div className="font-body-sm font-semibold text-on-surface uppercase mb-1 text-[11px] tracking-wider">
                  Landing &amp; Traverse Rec
                </div>
                <div className="flex justify-between items-center font-data-md bg-surface p-1.5 tech-border rounded-sm text-[13px] border-dashed">
                  <span className="text-on-surface-variant">Status:</span>
                  <span className="text-outline font-semibold">Not connected</span>
                </div>
                <div className="font-data-sm text-outline text-[11px] mt-1 px-1.5">
                  Needs slope/illumination model + rover path planner.
                </div>
              </div>
            </div>
          </div>

          <button className="w-full mt-4 py-2 bg-surface text-primary tech-border rounded font-body-sm font-semibold uppercase tracking-wider hover:bg-surface-container-high transition-colors text-[12px]">
            Export Report
          </button>
        </div>
      </div>
    </main>
  );
}