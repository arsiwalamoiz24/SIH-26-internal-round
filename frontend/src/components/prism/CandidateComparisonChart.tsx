"use client";

import { useMemo } from "react";
import {
  REAL_CANDIDATE_MARKER,
  SYNTHETIC_CANDIDATES,
  type CandidateMarker,
} from "@/data/prismDemoData";
import { DemoDataBadge } from "./DemoDataBadge";

export function CandidateComparisonChart() {
  const rows = useMemo(() => {
    const combined: CandidateMarker[] = [REAL_CANDIDATE_MARKER, ...SYNTHETIC_CANDIDATES];
    return [...combined].sort((a, b) => b.pv - a.pv).slice(0, 15);
  }, []);
  const maxPv = Math.max(...rows.map((r) => r.pv));

  return (
    <div className="bg-surface-container-lowest tech-border rounded p-4 flex flex-col gap-2">
      <div className="flex items-center justify-between pb-2 tech-border-b">
        <h3 className="font-h2 text-h2 text-on-surface uppercase tracking-tight m-0">
          Candidate Comparison — Pv (mean)
        </h3>
        <DemoDataBadge source="synthetic_demo" />
      </div>
      <p className="font-data-sm text-[10px] text-outline uppercase tracking-wider mb-1">
        Real candidate shown against fabricated comparison PSRs — for interaction demo only, not a
        real multi-candidate survey.
      </p>

      <div className="flex flex-col gap-1.5">
        {rows.map((r) => {
          const isReal = r.source === "real_pipeline";
          return (
            <div key={r.id} className="flex items-center gap-2">
              <div
                className={`w-32 shrink-0 font-data-sm text-[10px] truncate ${
                  isReal ? "text-primary font-semibold" : "text-on-surface-variant"
                }`}
                title={r.id}
              >
                {r.id}
              </div>
              <div className="flex-1 h-3.5 bg-surface-container-low rounded-sm overflow-hidden tech-border">
                <div
                  className={isReal ? "h-full bg-primary" : "h-full bg-outline-variant"}
                  style={{ width: `${(r.pv / maxPv) * 100}%` }}
                />
              </div>
              <div className="w-12 shrink-0 font-data-sm text-[10px] mono-nums text-right text-on-surface">
                {r.pv.toFixed(3)}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
