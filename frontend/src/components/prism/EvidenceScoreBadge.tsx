"use client";

import { useState } from "react";
import { EVIDENCE_SCORE_TOOLTIP, type EvidenceScore } from "@/data/prismDemoData";
import { DemoDataBadge } from "./DemoDataBadge";

export function EvidenceScoreBadge({ evidence }: { evidence: EvidenceScore }) {
  const [showTip, setShowTip] = useState(false);

  return (
    <div className="bg-surface-container-lowest tech-border rounded p-4 relative">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-1.5">
          <span className="font-data-sm text-outline uppercase text-[10px] tracking-wider">
            Physics Evidence Score
          </span>
          <button
            type="button"
            aria-label="What is the Physics Evidence Score?"
            onMouseEnter={() => setShowTip(true)}
            onMouseLeave={() => setShowTip(false)}
            onFocus={() => setShowTip(true)}
            onBlur={() => setShowTip(false)}
            className="material-symbols-outlined text-outline text-[14px] leading-none cursor-help"
          >
            info
          </button>
        </div>
        <DemoDataBadge source={evidence.source} />
      </div>

      {showTip && (
        <div className="absolute z-10 top-9 left-4 right-4 bg-inverse-surface text-inverse-on-surface text-[11px] font-body-sm rounded p-2 shadow-lg">
          {EVIDENCE_SCORE_TOOLTIP}
        </div>
      )}

      <div className="flex items-end justify-between">
        <div className="text-h1 font-h1 text-primary leading-none mono-nums">
          {evidence.score.toFixed(2)}
        </div>
        <div className="text-right">
          <div className="font-data-md text-data-md text-on-surface font-semibold">
            Rank {evidence.rank} / {evidence.outOf}
          </div>
          <div className="font-data-sm text-outline text-[10px] uppercase tracking-wider">
            shortlisted candidates
          </div>
        </div>
      </div>
      <div className="mt-2 pt-2 tech-border-t font-body-sm text-[11px] text-on-surface-variant">
        Not an ice probability or confidence score — a transparent, unweighted ranking of physics
        indicators across the shortlist.
      </div>
    </div>
  );
}
