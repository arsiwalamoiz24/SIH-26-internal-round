import type { MlAnomalyResult } from "@/data/prismDemoData";
import { ML_INTERPRETATION } from "@/data/prismDemoData";
import { DemoDataBadge } from "./DemoDataBadge";

export function MlPanel({ ml }: { ml: MlAnomalyResult }) {
  const pct = (ml.candidateRank / ml.nSamples) * 100;

  return (
    <div className="bg-surface-container-lowest tech-border rounded p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between pb-2 tech-border-b">
        <h3 className="font-h2 text-h2 text-on-surface uppercase tracking-tight m-0">
          ML Anomaly Ranking
        </h3>
        <DemoDataBadge source={ml.source} />
      </div>

      <div className="font-data-sm text-outline uppercase text-[10px] tracking-wider">
        {ml.method} · {ml.nSamples} PSRs analyzed
      </div>

      <div className="flex items-center gap-3">
        <div className="text-data-lg font-data-lg text-primary font-semibold mono-nums">
          Rank {ml.candidateRank} / {ml.nSamples}
        </div>
        <div className="flex-1 h-2 bg-surface-container-low rounded-full overflow-hidden tech-border">
          <div
            className="h-full bg-primary"
            style={{ width: `${Math.max(4, 100 - pct)}%` }}
            aria-hidden
          />
        </div>
      </div>

      <div className="font-body-sm text-[11px] text-on-surface-variant pt-1 tech-border-t">
        {ML_INTERPRETATION}
      </div>
      <div className="font-data-sm text-[10px] text-outline uppercase tracking-wider">
        Anomaly ranking — not an ice classifier
      </div>
    </div>
  );
}
