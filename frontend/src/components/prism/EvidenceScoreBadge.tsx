"use client";

import { useState } from "react";
import { EVIDENCE_SCORE_TOOLTIP, type EvidenceScore } from "@/data/prismDemoData";

/**
 * Instrument-style readout, not a scorecard. No border/background of its
 * own -- whitespace and typography establish hierarchy, matching the
 * "PHYSICS EVIDENCE / 1.00 / RANK 01/07" instrument-reading treatment.
 */
export function EvidenceScoreBadge({ evidence }: { evidence: EvidenceScore }) {
  const [showTip, setShowTip] = useState(false);
  const rankPadded = String(evidence.rank).padStart(2, "0");
  const outOfPadded = String(evidence.outOf).padStart(2, "0");

  return (
    <div className="relative flex flex-col gap-3 py-1">
      <div className="flex items-center gap-1.5">
        <span className="coord-label">Physics Evidence</span>
        <button
          type="button"
          aria-label="What is the Physics Evidence Score?"
          onMouseEnter={() => setShowTip(true)}
          onMouseLeave={() => setShowTip(false)}
          onFocus={() => setShowTip(true)}
          onBlur={() => setShowTip(false)}
          className="material-symbols-outlined text-outline text-[13px] leading-none cursor-help"
        >
          info
        </button>
      </div>

      {showTip && (
        <div className="absolute z-10 top-7 left-0 right-0 bg-inverse-surface text-inverse-on-surface text-[11px] font-body-sm rounded p-2 shadow-lg">
          {EVIDENCE_SCORE_TOOLTIP}
        </div>
      )}

      <div className="readout-value text-[52px]">{evidence.score.toFixed(2)}</div>

      <div className="flex items-baseline gap-2">
        <span className="font-data-md text-[13px] text-on-surface font-semibold mono-nums">
          Rank {rankPadded} / {outOfPadded}
        </span>
        <span className="text-[11px] text-on-surface-variant">shortlisted candidates</span>
      </div>

      <div className="text-[11px] text-on-surface-variant leading-relaxed max-w-[36ch]">
        Not an ice probability — a transparent, unweighted ranking of physics indicators
        across the shortlist.
      </div>
    </div>
  );
}
