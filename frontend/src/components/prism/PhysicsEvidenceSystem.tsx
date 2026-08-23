import type { RadarMetric } from "@/data/prismDemoData";

interface Indicator {
  label: string;
  metric: RadarMetric;
  interpretation: string;
  flagged?: boolean;
}

/**
 * Pv / CPR / SERD / T-Ratio as ONE analytical system, not four separate
 * cards -- internal hairline dividers instead of nested bordered boxes.
 * Replaces the four PhysicsEvidenceCard instances previously rendered
 * side by side in page.tsx.
 */
export function PhysicsEvidenceSystem({ indicators }: { indicators: Indicator[] }) {
  return (
    <div className="bento-card">
      <div className="bento-header">
        <h3 className="text-[13px] font-semibold text-on-surface tracking-tight m-0">Physics Evidence</h3>
        <span className="coord-label">Radar-derived indicators</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 field-divide">
        {indicators.map((ind) => (
          <div key={ind.label} className="p-4 flex flex-col gap-2">
            <div className="flex items-center gap-1.5">
              <span className="coord-label">{ind.label}</span>
              {ind.flagged && (
                <span className="w-1.5 h-1.5 rounded-full bg-error shrink-0" title="Flagged for investigation" />
              )}
            </div>

            <div className="flex items-baseline gap-1.5">
              <span className="font-data-lg text-[20px] font-semibold mono-nums text-primary">
                {ind.metric.mean.toFixed(3)}
              </span>
              <span className="text-[10px] text-on-surface-variant">mean</span>
            </div>

            <div className="flex justify-between text-[11px] text-on-surface-variant">
              <span>
                median <span className="mono-nums text-on-surface">{ind.metric.median.toFixed(3)}</span>
              </span>
              <span className={ind.flagged ? "text-error font-semibold" : ""}>
                {ind.metric.percentile.toFixed(1)}
                <sup>{ordinalSuffix(ind.metric.percentile)}</sup> pct
              </span>
            </div>

            <p className="text-[11px] text-on-surface-variant leading-snug m-0">{ind.interpretation}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function ordinalSuffix(n: number): string {
  const v = Math.round(n) % 100;
  if (v >= 11 && v <= 13) return "th";
  switch (Math.round(n) % 10) {
    case 1:
      return "st";
    case 2:
      return "nd";
    case 3:
      return "rd";
    default:
      return "th";
  }
}
