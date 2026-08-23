import type { MlAnomalyResult } from "@/data/prismDemoData";
import { ML_INTERPRETATION } from "@/data/prismDemoData";

/**
 * Sits directly beneath EvidenceScoreBadge in the hero column, separated
 * by a hairline rule (see page.tsx) rather than being its own card --
 * the pair should read as one instrument stack, not two widgets.
 */
export function MlPanel({ ml }: { ml: MlAnomalyResult }) {
  const pct = (ml.candidateRank / ml.nSamples) * 100;

  return (
    <div className="flex flex-col gap-2 py-1">
      <div className="coord-label">ML Anomaly Ranking</div>
      <div className="text-[10px] text-on-surface-variant">
        {ml.method} · {ml.nSamples} PSRs analyzed
      </div>

      <div className="flex items-center gap-3">
        <div className="font-data-md text-[15px] text-on-surface font-semibold mono-nums whitespace-nowrap">
          {ml.candidateRank} / {ml.nSamples}
        </div>
        <div className="flex-1 h-1 bg-surface-container-low overflow-hidden rounded-full">
          <div className="h-full bg-primary" style={{ width: `${Math.max(4, 100 - pct)}%` }} aria-hidden />
        </div>
      </div>

      <div className="text-[11px] text-on-surface-variant leading-relaxed">{ML_INTERPRETATION}</div>
    </div>
  );
}
