"use client";

import { useState } from "react";
import Link from "next/link";
import { getLandingSites, getTargetCrater, LandingSite } from "@/lib/api";
import { IllustrativeBanner } from "@/components/prism/IllustrativeBanner";
import "material-symbols";

export default function LandingSitePage() {
  const sites = getLandingSites();
  const target = getTargetCrater();

  const [selectedSiteId, setSelectedSiteId] = useState<string>(sites[0]?.id || "site-alpha");
  const selected = sites.find((s) => s.id === selectedSiteId) || sites[0];

  return (
    <main className="flex-1 p-4 flex gap-4 overflow-hidden bg-background h-[calc(100vh-80px)]">
      {/* ===================== LEFT COLUMN (~58%) ===================== */}
      <section className="w-[58%] flex flex-col gap-3 h-full min-h-0">
        <div className="shrink-0 flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <h1 className="text-[24px] font-semibold text-on-background m-0 leading-tight">
              Landing Site Selection ({target.psrId})
            </h1>
            <span className="bg-surface-container-high text-on-surface border tech-border text-[9px] font-mono font-bold px-1.5 py-0.5 rounded">
              DERIVED MODEL
            </span>
          </div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.08em] text-outline mt-1">
            RADAR SURFACE SAFETY • P(ICE) PROXIMITY • LOLA REFERENCE BASELINE • FR-3
          </p>
          <IllustrativeBanner detail="The basemap image is a stylized reference, not satellite imagery, and site marker positions on it are schematic (not plotted to exact coordinates)." />
        </div>

        {/* Hero Map */}
        <div className="flex-1 bento-card-surface flex flex-col relative overflow-hidden min-h-0">
          <div className="absolute top-0 left-0 right-0 z-10 px-3 py-2 bg-surface/95 backdrop-blur-sm tech-border-b flex justify-between items-center">
            <span className="text-[11px] font-bold uppercase tracking-wider text-on-surface font-mono">
              TARGET CRATER RIM BUFFER • CANDIDATE SITES
            </span>
            <span className="text-[11px] font-mono text-primary font-bold">
              CENTER: {Math.abs(target.latitude)}° S, {target.longitude}° E
            </span>
          </div>

          <div
            className="absolute inset-0 bg-cover bg-center"
            style={{
              backgroundImage:
                "url('https://lh3.googleusercontent.com/aida-public/AB6AXuDmIfcEcb0d3gJHtgpkp9oi7FPIqApCxKptDI0YAmAGGjl0u8fQVcT2uSv6QHpa_1b0KXoiBfhaeVnCXDSJ6qXJb2K5S2qYRUTDOpqfEa9P7ZAXL_xXVXMOs42-lTj25CSLuiJvPW6dBpglhi8uhe84MqtDhUyKQaki_TbRyzgpV_JwIXFWlpq0ySZxrOxw_PPLSY1IMf-oOF4ulSnQDTPIn46qvgguUT-LSg4CXGzEJnASixIrdk4e')",
            }}
          />
          <div
            className="absolute inset-0 opacity-25 pointer-events-none"
            style={{
              backgroundImage:
                "linear-gradient(to right, var(--color-outline-variant) 1px, transparent 1px), linear-gradient(to bottom, var(--color-outline-variant) 1px, transparent 1px)",
              backgroundSize: "20px 20px",
            }}
          />

          <div className="absolute inset-0 z-10 pointer-events-none">
            {/* Site Alpha */}
            <div className="absolute top-[35%] left-[32%] -translate-x-1/2 -translate-y-1/2 flex flex-col items-center">
              <div className="w-8 h-8 rounded-full border-2 border-primary bg-primary/25 flex items-center justify-center animate-pulse">
                <div className="w-2.5 h-2.5 bg-primary rounded-full" />
              </div>
              <span className="mt-1 bg-surface tech-border text-primary px-2 py-0.5 rounded text-[9px] font-bold uppercase shadow-sm">
                SITE ALPHA (PRIMARY)
              </span>
            </div>
            {/* Site Beta */}
            <div className="absolute top-[28%] left-[62%] -translate-x-1/2 -translate-y-1/2 flex flex-col items-center opacity-85">
              <div className="w-5 h-5 rounded-full border border-outline bg-surface/70 flex items-center justify-center">
                <div className="w-1.5 h-1.5 bg-outline rounded-full" />
              </div>
              <span className="mt-1 text-on-surface-variant text-[9px] font-bold uppercase bg-surface/90 px-1 rounded shadow-xs">
                SITE BETA
              </span>
            </div>
            {/* Site Gamma */}
            <div className="absolute top-[68%] left-[45%] -translate-x-1/2 -translate-y-1/2 flex flex-col items-center opacity-85">
              <div className="w-5 h-5 rounded-full border border-outline bg-surface/70 flex items-center justify-center">
                <div className="w-1.5 h-1.5 bg-outline rounded-full" />
              </div>
              <span className="mt-1 text-on-surface-variant text-[9px] font-bold uppercase bg-surface/90 px-1 rounded shadow-xs">
                SITE GAMMA
              </span>
            </div>
          </div>
        </div>

        {/* Comparison Matrix */}
        <div className="bento-card flex flex-col shrink-0 mb-4">
          <div className="bento-header">
            <span className="text-[11px] font-bold uppercase tracking-wider text-on-surface font-mono">
              CANDIDATE COMPARISON MATRIX
            </span>
            <span className="text-[9px] font-mono text-outline uppercase font-bold">
              DERIVED PROXIMITY MODEL
            </span>
          </div>
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="tech-border-b bg-surface-container-lowest">
                <th className="text-[10px] font-normal uppercase text-outline px-3 py-1.5">Site ID</th>
                <th className="text-[10px] font-normal uppercase text-outline px-3 py-1.5 text-right">LOLA Slope (Ref)</th>
                <th className="text-[10px] font-normal uppercase text-outline px-3 py-1.5 text-right">Dist to Ice Peak</th>
                <th className="text-[10px] font-normal uppercase text-outline px-3 py-1.5 text-right">Sunlight</th>
                <th className="text-[10px] font-normal uppercase text-outline px-3 py-1.5 text-right">Safety Score</th>
                <th className="text-[10px] font-normal uppercase text-outline px-3 py-1.5 text-center">Rank</th>
              </tr>
            </thead>
            <tbody className="font-mono text-[12px]">
              {sites.map((site) => {
                const isActive = site.id === selectedSiteId;
                return (
                  <tr
                    key={site.id}
                    onClick={() => setSelectedSiteId(site.id)}
                    className={`tech-border-b last:border-b-0 cursor-pointer transition-colors ${
                      isActive ? "bg-primary-fixed text-on-primary-fixed" : "hover:bg-surface-container"
                    }`}
                  >
                    <td className="px-3 py-2 relative">
                      {isActive && (
                        <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary" />
                      )}
                      <span className={`font-medium ${isActive ? "text-primary font-bold" : "text-on-surface-variant"}`}>
                        {site.name}
                      </span>
                    </td>
                    <td className={`px-3 py-2 text-right ${site.slope > 15 ? "text-tertiary" : ""}`}>
                      {site.slope}°
                    </td>
                    <td className={`px-3 py-2 text-right ${site.distToIce > 3 ? "text-error" : ""}`}>
                      {site.distToIce} km
                    </td>
                    <td className="px-3 py-2 text-right">{site.sunlight} h/d</td>
                    <td className={`px-3 py-2 text-right font-medium ${isActive ? "text-secondary font-bold" : ""}`}>
                      {site.safetyScore}%
                    </td>
                    <td className={`px-3 py-2 text-center font-bold ${isActive ? "text-primary" : "text-outline"}`}>
                      {site.rank}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {/* ===================== RIGHT COLUMN (~42%) ===================== */}
      <section className="w-[42%] flex flex-col h-full min-h-0">
        <div className="bento-card flex flex-col h-full mb-4 overflow-hidden">
          {/* Header + ring */}
          <div className="px-4 pt-3.5 pb-3 tech-border-b shrink-0 bg-surface-container-lowest">
            <div className="flex justify-between items-start mb-2.5">
              <div>
                <span className="inline-block bg-primary-fixed text-on-primary-fixed-variant text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded mb-1">
                  {selected.rank === 1 ? "PRIMARY RECOMMENDATION" : `CANDIDATE RANK #${selected.rank}`}
                </span>
                <h2 className="text-[17px] font-semibold text-on-background m-0">
                  {selected.name}
                </h2>
              </div>
              <span className="material-symbols-outlined text-primary text-[22px]">verified</span>
            </div>

            <div className="flex items-center gap-3">
              <div className="relative w-13 h-13 shrink-0">
                <svg className="w-13 h-13 -rotate-90" viewBox="0 0 56 56">
                  <circle cx="28" cy="28" r="24" fill="none" stroke="var(--color-outline-variant)" strokeWidth="3.5" />
                  <circle
                    cx="28"
                    cy="28"
                    r="24"
                    fill="none"
                    stroke="var(--color-primary)"
                    strokeWidth="3.5"
                    strokeDasharray={`${(selected.safetyScore / 100) * 151} 151`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-[13px] font-mono font-bold text-primary">
                    {selected.safetyScore}%
                  </span>
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <span className="block text-[9px] font-bold uppercase tracking-wider text-outline mb-0.5 font-mono">
                  SAFETY SCORING RATIONALE
                </span>
                <p className="text-[11px] text-on-surface-variant m-0 leading-snug">
                  {selected.rationale}
                </p>
              </div>
            </div>
          </div>

          {/* 2×2 metrics */}
          <div className="px-4 py-2.5 grid grid-cols-2 gap-2 tech-border-b shrink-0 font-mono bg-surface-container-lowest">
            <div className="bg-surface-container tech-border rounded px-2.5 py-1.5">
              <span className="text-[9px] uppercase text-outline block mb-0.5">SLOPE (LOLA REF)</span>
              <span className="block text-[15px] font-medium text-on-background">{selected.slope}°</span>
              <span className="text-[9px] text-secondary">
                {selected.slope <= 15 ? "Within 15° limit" : "Elevated incline"}
              </span>
            </div>
            <div className="bg-surface-container tech-border rounded px-2.5 py-1.5">
              <span className="text-[9px] uppercase text-outline block mb-0.5">DIST TO ICE PEAK</span>
              <span className="block text-[15px] font-medium text-on-background">{selected.distToIce} km</span>
              <span className="text-[9px] text-secondary">
                {selected.distToIce <= 2 ? "Direct corridor" : "Extended traverse"}
              </span>
            </div>
            <div className="bg-surface-container tech-border rounded px-2.5 py-1.5">
              <span className="text-[9px] uppercase text-outline block mb-0.5">SUNLIGHT / POWER</span>
              <span className="block text-[15px] font-medium text-on-background">{selected.sunlight} h/d</span>
              <span className="text-[9px] text-secondary">
                {selected.sunlight >= 10 ? "Power surplus" : "Limited solar window"}
              </span>
            </div>
            <div className="bg-surface-container tech-border rounded px-2.5 py-1.5">
              <span className="text-[9px] uppercase text-outline block mb-0.5">RADAR ROUGHNESS</span>
              <span className="block text-[12px] font-medium text-tertiary">
                Illustrative proxy
              </span>
              <span className="text-[9px] text-tertiary">
                Derived from safety score, not a measured roughness metric
              </span>
            </div>
          </div>

          {/* Scoring breakdown */}
          <div className="px-4 py-3 tech-border-b shrink-0 flex flex-col gap-2 bg-surface-container-lowest">
            <span className="text-[12px] font-bold uppercase tracking-wider text-on-background font-mono">
              SCORING BREAKDOWN (DERIVED WEIGHTED)
            </span>
            <div>
              <div className="flex justify-between text-[11px] font-mono text-on-surface-variant mb-1">
                <span>SLOPE SAFETY (40%)</span>
                <span>{selected.scoringBreakdown?.slopeSafetyScore ?? "—"}/100</span>
              </div>
              <div className="h-1 bg-surface-variant rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary rounded-full"
                  style={{ width: `${selected.scoringBreakdown?.slopeSafetyScore ?? 0}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-[11px] font-mono text-on-surface-variant mb-1">
                <span>ICE PROXIMITY (35%)</span>
                <span>{selected.scoringBreakdown?.iceProximityScore ?? "—"}/100</span>
              </div>
              <div className="h-1 bg-surface-variant rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary-container rounded-full"
                  style={{ width: `${selected.scoringBreakdown?.iceProximityScore ?? 0}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-[11px] font-mono text-on-surface-variant mb-1">
                <span>POWER / SUNLIGHT (25%)</span>
                <span>{selected.scoringBreakdown?.powerSunlightScore ?? "—"}/100</span>
              </div>
              <div className="h-1 bg-surface-variant rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary-fixed rounded-full"
                  style={{ width: `${selected.scoringBreakdown?.powerSunlightScore ?? 0}%` }}
                />
              </div>
            </div>
          </div>

          {/* Buttons */}
          <div className="px-4 py-3 tech-border-t shrink-0 flex flex-col items-center justify-center gap-2 bg-surface-container-lowest mt-auto">
            <Link
              href="/rover-traverse"
              className="w-full bg-primary hover:opacity-90 text-on-primary text-[11px] font-bold uppercase tracking-wider py-2.5 rounded transition-opacity text-center"
            >
              PROCEED TO ROVER TRAVERSE PLANNING
            </Link>

            <button className="w-full bg-transparent hover:bg-surface text-primary border border-primary text-[11px] font-bold uppercase tracking-wider py-1.5 rounded transition-colors">
              EXPORT SITE REPORT (JSON / PDF)
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}
