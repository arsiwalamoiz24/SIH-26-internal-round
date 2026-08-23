"use client";

import { useState } from "react";
import PathImage from "@/assets/path.png";
import { getRoverPaths, getTargetCrater, RoverPath } from "@/lib/api";
import { REAL_CANDIDATE } from "@/data/prismDemoData";
import { IllustrativeBanner } from "@/components/prism/IllustrativeBanner";

export default function HazardTraverse() {
  const target = getTargetCrater();
  const paths = getRoverPaths();
  const [activePathId, setActivePathId] = useState<string>("path-discovery");

  const activePath = paths.find((p) => p.id === activePathId) || paths[0];

  return (
    <main className="flex-1 p-4 flex gap-4 overflow-hidden bg-background h-[calc(100vh-80px)] mb-3">
      <section className="flex-1 flex flex-col h-full gap-3">
        <div className="bento-card p-4 shrink-0">
          <div className="flex justify-between items-start">
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-[22px] font-semibold text-on-background m-0 leading-tight">
                  Hazard Spotting &amp; Rover Traverse ({target.psrId})
                </h1>
                <span className="bg-primary-fixed text-on-primary-fixed-variant tech-border border text-[9px] font-mono font-bold px-1.5 py-0.5 rounded">
                  PARETO GRAPH MODEL
                </span>
              </div>
              <div className="text-[11px] font-mono text-outline uppercase tracking-wider mt-1">
                Optical Context (OHRC Pending) • DFSAR Radar Roughness Proxy • Multi-Objective Trajectories • FR-4
              </div>
            </div>
            {/* Path selector tabs */}
            <div className="flex gap-1.5 font-mono text-[11px]">
              {paths.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setActivePathId(p.id)}
                  className={`px-2.5 py-1 rounded font-semibold transition-all ${
                    activePathId === p.id
                      ? "bg-primary text-on-primary shadow-xs"
                      : "bg-surface-container text-on-surface-variant hover:bg-surface-container-high"
                  }`}
                >
                  {p.type.toUpperCase()} ({p.lengthKm} KM)
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="relative flex-1 min-h-0 bg-[#1a1a1a] rounded-lg bottom-2 shrink-0 overflow-hidden shadow-inner">
          <img
            src={PathImage.src}
            alt="Optical Context Reference with Radar Hazard Overlay"
            className="w-full h-full object-cover absolute top-0 left-0 rounded-lg opacity-90"
          />
          <div className="absolute top-3 left-3 bg-black/80 backdrop-blur-md text-white font-mono text-[10px] px-2.5 py-1.5 rounded border border-white/20">
            <span className="text-emerald-400 font-bold">ACTIVE PATH:</span> {activePath.name.toUpperCase()} • LENGTH {activePath.lengthKm} KM
          </div>
        </div>
      </section>

      <section className="w-[320px] flex flex-col gap-3 h-full min-h-0 shrink-0">
        <IllustrativeBanner detail="The traverse cost breakdown below (shadow exposure %, roughness tier, P(Ice) yield) is a static illustrative weighting, not computed from the pipeline for each path." />

        <div className="bento-card p-3 shrink-0">
          <div className="flex justify-between items-center mb-2">
            <span className="text-[12px] font-semibold text-on-background font-mono">
              RADAR HAZARD SUMMARY
            </span>
            <span className="text-[9px] font-mono text-outline uppercase font-bold">
              REAL PIPELINE (SP_840980_0797630)
            </span>
          </div>
          <div className="grid grid-cols-2 gap-1.5">
            <div className="bg-surface-container tech-border rounded px-2 py-1.5">
              <div className="text-[9px] text-outline uppercase tracking-wider font-mono">
                Terrain Roughness (TRI)
              </div>
              <div className="text-[14px] font-mono font-semibold text-on-background">
                {REAL_CANDIDATE.terrain.triMeters.toFixed(1)} <span className="text-[10px] text-outline">m</span>
              </div>
            </div>
            <div className="bg-surface-container tech-border rounded px-2 py-1.5">
              <div className="text-[9px] text-outline uppercase tracking-wider font-mono">
                Mean PSR Slope
              </div>
              <div className="text-[14px] font-mono font-semibold text-on-background">
                {REAL_CANDIDATE.terrain.meanSlopeDeg.toFixed(1)}° <span className="text-[10px] text-outline">Real</span>
              </div>
            </div>
            <div className="bg-surface-container tech-border rounded px-2 py-1.5 col-span-2">
              <div className="text-[9px] text-tertiary uppercase tracking-wider font-mono">
                Approach Pass &amp; Terrain Clearance
              </div>
              <div className="text-[12px] font-mono font-semibold text-tertiary">
                Illustrative only — not present in pipeline output
              </div>
            </div>
          </div>
        </div>

        {/* Traverse Cost Breakdown */}
        <div className="bento-card p-3 shrink-0">
          <div className="flex justify-between items-center mb-2">
            <span className="text-[12px] font-semibold text-on-background font-mono">
              TRAVERSE COST BREAKDOWN
            </span>
            <span className="text-[9px] font-mono text-outline font-bold">ILLUSTRATIVE MODEL</span>
          </div>

          <div className="flex flex-col gap-2 font-mono">
            <div>
              <div className="flex justify-between text-[11px] mb-0.5">
                <span className="text-on-surface-variant">Double-bounce Roughness</span>
                <span className="text-tertiary font-medium">Moderate</span>
              </div>
              <div className="h-1 bg-surface-variant rounded-full overflow-hidden">
                <div className="h-full bg-tertiary rounded-full" style={{ width: activePathId === "path-safety" ? "25%" : "45%" }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-[11px] mb-0.5">
                <span className="text-on-surface-variant">PSR Shadow Exposure</span>
                <span className="text-error font-medium">65% Shadow</span>
              </div>
              <div className="h-1 bg-surface-variant rounded-full overflow-hidden">
                <div className="h-full bg-error rounded-full" style={{ width: "65%" }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-[11px] mb-0.5">
                <span className="text-on-surface-variant">P(Ice) Exposure Yield</span>
                <span className="text-primary font-medium">{activePathId === "path-discovery" ? "Maximum" : "Moderate"}</span>
              </div>
              <div className="h-1 bg-surface-variant rounded-full overflow-hidden">
                <div className="h-full bg-primary rounded-full" style={{ width: activePathId === "path-discovery" ? "92%" : "70%" }} />
              </div>
            </div>

            <div className="pt-1.5 mt-0.5 tech-border-t flex justify-between items-center">
              <span className="text-[10px] text-outline uppercase tracking-wider">
                Total Path Cost Score
              </span>
              <span className="text-[16px] font-mono font-bold text-on-background">{activePath.traverseCost}</span>
            </div>
          </div>
        </div>

        {/* Path Details */}
        <div className="bento-card flex flex-col flex-1 mb-3 overflow-hidden">
          <div className="bento-header shrink-0">
            <div className="text-[11px] font-semibold text-on-surface uppercase font-mono">
              Waypoints ({activePath.waypoints.length})
            </div>
            <div className="text-[12px] font-mono font-semibold text-primary">
              {activePath.lengthKm} KM
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-3">
            <div className="flex flex-col">
              {activePath.waypoints.map((wp, idx) => (
                <div key={wp.id} className="flex gap-2.5">
                  <div className="flex flex-col items-center">
                    <div
                      className={`w-2.5 h-2.5 rounded-full border-2 shrink-0 ${
                        idx === 0
                          ? "bg-primary border-primary"
                          : idx === activePath.waypoints.length - 1
                          ? "bg-error border-error"
                          : "bg-surface-container-lowest border-outline-variant"
                      }`}
                    />
                    {idx < activePath.waypoints.length - 1 && (
                      <div className="w-px flex-1 bg-outline-variant min-h-[22px]" />
                    )}
                  </div>

                  <div className="pb-2.5">
                    <div className="text-[11px] font-semibold text-on-background font-mono">
                      {wp.id}: {wp.title}
                    </div>
                    <div className="text-[10px] text-on-surface-variant mt-0.5">{wp.note}</div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-1 pt-2 tech-border-t">
              <div className="text-[9px] text-outline uppercase tracking-wider mb-1 font-mono">
                Radar Pv Intensity Along Path
              </div>
              <div className="h-9 bg-surface-container tech-border rounded relative overflow-hidden flex items-end px-1 gap-1">
                {activePath.waypoints.map((wp, i) => (
                  <div
                    key={i}
                    className="flex-1 bg-primary/70 rounded-t"
                    style={{ height: `${(wp.localPv / 0.8) * 100}%` }}
                    title={`${wp.title}: Pv=${wp.localPv}`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}