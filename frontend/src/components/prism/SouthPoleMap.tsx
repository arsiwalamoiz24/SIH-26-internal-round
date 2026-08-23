"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import {
  REAL_CANDIDATE_MARKER,
  SYNTHETIC_CANDIDATES,
  type CandidateMarker,
  type CandidateStatus,
  type SyntheticCandidate,
} from "@/data/prismDemoData";
import { DemoDataBadge } from "./DemoDataBadge";

type StatusFilter = CandidateStatus | "all";

const STATUS_COLOR: Record<CandidateStatus, string> = {
  potential_ice_candidate: "var(--color-primary)",
  under_review: "var(--color-tertiary)",
  low_priority: "var(--color-outline)",
};

const STATUS_LABEL: Record<CandidateStatus, string> = {
  potential_ice_candidate: "Potential Ice Candidate",
  under_review: "Under Review",
  low_priority: "Low Priority",
};

const VIEWBOX = 400;
const CENTER = VIEWBOX / 2;
const PX_PER_DEG_COLAT = 18;

function project(lat: number, lon: number) {
  const colat = 90 + lat; // degrees from south pole (lat is negative near -90)
  const r = colat * PX_PER_DEG_COLAT;
  const theta = (lon * Math.PI) / 180;
  return {
    x: CENTER + r * Math.cos(theta),
    y: CENTER + r * Math.sin(theta),
  };
}

export function SouthPoleMap() {
  const allCandidates: CandidateMarker[] = useMemo(
    () => [REAL_CANDIDATE_MARKER, ...SYNTHETIC_CANDIDATES],
    []
  );
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [selectedId, setSelectedId] = useState<string>(REAL_CANDIDATE_MARKER.id);

  const visible = allCandidates.filter(
    (c) => statusFilter === "all" || c.status === statusFilter
  );
  const selected = allCandidates.find((c) => c.id === selectedId) ?? REAL_CANDIDATE_MARKER;

  const rings = [2, 4, 6, 8, 10];

  return (
    <div className="viewport-frame bg-surface h-full flex flex-col">
      <div className="flex justify-between items-center px-4 py-2 border-b border-outline-variant shrink-0">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-outline text-[18px]">public</span>
          <span className="font-body-md font-semibold text-on-surface uppercase tracking-wider text-[13px]">
            South Pole Candidate Map
          </span>
        </div>
        <div className="flex gap-1 bg-surface-container-low rounded p-0.5">
          {(["all", "potential_ice_candidate", "under_review", "low_priority"] as StatusFilter[]).map(
            (key) => (
              <button
                key={key}
                onClick={() => setStatusFilter(key)}
                className={`px-2 py-1 rounded-sm font-data-sm text-[10px] uppercase tracking-wide transition-colors ${
                  statusFilter === key
                    ? "bg-primary text-on-primary font-semibold"
                    : "text-on-surface-variant hover:bg-surface-container-high"
                }`}
              >
                {key === "all" ? "All" : STATUS_LABEL[key]}
              </button>
            )
          )}
        </div>
      </div>

      <div className="flex flex-1 min-h-0">
        <div className="flex-1 min-w-0 relative bg-[#0a0e17]">
          <svg viewBox={`0 0 ${VIEWBOX} ${VIEWBOX}`} className="w-full h-full">
            {rings.map((deg) => (
              <circle
                key={deg}
                cx={CENTER}
                cy={CENTER}
                r={deg * PX_PER_DEG_COLAT}
                fill="none"
                stroke="#2a3242"
                strokeWidth={1}
              />
            ))}
            <circle cx={CENTER} cy={CENTER} r={3} fill="#5b6474" />
            <text x={CENTER + 6} y={CENTER - 6} fill="#5b6474" fontSize={9} fontFamily="monospace">
              90°S
            </text>

            {visible.map((c) => {
              const { x, y } = project(c.latitude, c.longitude);
              const isReal = c.source === "real_pipeline";
              const isSelected = c.id === selectedId;
              return (
                <g key={c.id} onClick={() => setSelectedId(c.id)} className="cursor-pointer">
                  {isSelected && (
                    <circle cx={x} cy={y} r={isReal ? 12 : 9} fill="none" stroke="#ffffff" strokeWidth={1} opacity={0.6} />
                  )}
                  <circle
                    cx={x}
                    cy={y}
                    r={isReal ? 7 : 4.5}
                    fill={STATUS_COLOR[c.status]}
                    stroke={isReal ? "#ffffff" : "none"}
                    strokeWidth={isReal ? 1.5 : 0}
                    opacity={isReal ? 1 : 0.85}
                  />
                </g>
              );
            })}
          </svg>

          <div className="absolute bottom-2 left-2 bg-black/60 backdrop-blur-sm rounded px-2 py-1 flex gap-3 font-data-sm text-[10px] text-white/80">
            <LegendDot color="var(--color-primary)" label="Potential" />
            <LegendDot color="var(--color-tertiary)" label="Review" />
            <LegendDot color="var(--color-outline)" label="Low priority" />
          </div>
          <div className="absolute top-2 right-2">
            <DemoDataBadge source="synthetic_demo" className="opacity-90" />
          </div>
        </div>

        <div className="w-[220px] shrink-0 tech-border-l p-3 flex flex-col gap-2 overflow-y-auto">
          <div className="flex items-center justify-between">
            <span className="font-data-sm text-[11px] font-semibold text-on-surface truncate">
              {selected.id}
            </span>
            <DemoDataBadge source={selected.source} />
          </div>
          <div className="font-data-sm text-[11px] text-on-surface-variant mono-nums">
            {selected.latitude.toFixed(3)}°, {selected.longitude.toFixed(3)}°
          </div>
          <div className="grid grid-cols-2 gap-1 font-data-sm text-[10px] text-on-surface-variant">
            <div>Pv <span className="mono-nums text-on-surface">{selected.pv.toFixed(3)}</span></div>
            <div>CPR <span className="mono-nums text-on-surface">{selected.cpr.toFixed(3)}</span></div>
            <div>SERD <span className="mono-nums text-on-surface">{selected.serd.toFixed(3)}</span></div>
            <div>T-Ratio <span className="mono-nums text-on-surface">{selected.t_ratio.toFixed(3)}</span></div>
          </div>
          <Link
            href={`/candidate/${selected.id}`}
            className="mt-1 text-center py-1.5 bg-surface text-primary tech-border rounded font-body-sm font-semibold uppercase tracking-wider hover:bg-surface-container-high transition-colors text-[11px]"
          >
            View Report
          </Link>
          <div className="mt-2 pt-2 tech-border-t font-data-sm text-[10px] text-outline">
            {visible.length} candidates shown
          </div>
        </div>
      </div>
    </div>
  );
}

function LegendDot({ color, label }: { color: string; label: string }) {
  return (
    <span className="flex items-center gap-1">
      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
      {label}
    </span>
  );
}

export type { SyntheticCandidate };
