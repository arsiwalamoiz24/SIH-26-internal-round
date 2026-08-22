import type { RadarMetric } from "@/data/prismDemoData";
import { DemoDataBadge } from "./DemoDataBadge";

export function PhysicsEvidenceCard({
  label,
  metric,
  interpretation,
  flagged = false,
}: {
  label: string;
  metric: RadarMetric;
  interpretation: string;
  flagged?: boolean;
}) {
  return (
    <div
      className={`bg-surface-container-lowest tech-border rounded p-3 flex flex-col gap-2 ${
        flagged ? "border-l-2 border-l-error" : ""
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="font-data-sm text-outline uppercase text-[10px] tracking-wider">
          {label}
        </span>
        <DemoDataBadge source={metric.source} />
      </div>

      <div className="flex items-baseline gap-2">
        <span className="text-data-lg font-data-lg text-primary font-semibold mono-nums">
          {metric.mean.toFixed(3)}
        </span>
        <span className="font-data-sm text-on-surface-variant text-[11px]">mean</span>
      </div>

      <div className="grid grid-cols-2 gap-1 font-data-sm text-[11px] text-on-surface-variant">
        <div>
          median <span className="mono-nums text-on-surface">{metric.median.toFixed(3)}</span>
        </div>
        <div className={flagged ? "text-error font-semibold" : ""}>
          {metric.percentile.toFixed(1)}
          <sup>{ordinalSuffix(metric.percentile)}</sup> pct
        </div>
      </div>

      <div className="font-body-sm text-[11px] text-on-surface-variant pt-1 tech-border-t">
        {interpretation}
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
