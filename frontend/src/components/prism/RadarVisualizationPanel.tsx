import type { RealCandidate } from "@/data/prismDemoData";
import { DemoDataBadge } from "./DemoDataBadge";

export function RadarVisualizationPanel({ candidate }: { candidate: RealCandidate }) {
  return (
    <div className="bg-surface-container-lowest tech-border rounded p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between pb-2 tech-border-b">
        <h3 className="font-h2 text-h2 text-on-surface uppercase tracking-tight m-0">
          Radar Visualization
        </h3>
        <DemoDataBadge source="real_pipeline" />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <figure className="m-0 rounded-sm overflow-hidden tech-border">
          <img
            src={candidate.images.overview}
            alt="Candidate overview: Pv, CPR, SERD, boundary and coordinate"
            className="w-full h-48 object-cover"
          />
          <figcaption className="font-data-sm text-[10px] text-on-surface-variant p-1.5 tech-border-t">
            Pv / CPR / SERD, candidate boundary and coordinate
          </figcaption>
        </figure>
        <figure className="m-0 rounded-sm overflow-hidden tech-border">
          <img
            src={candidate.images.radarMetrics}
            alt="Candidate radar metrics composite"
            className="w-full h-48 object-cover"
          />
          <figcaption className="font-data-sm text-[10px] text-on-surface-variant p-1.5 tech-border-t">
            Radar physics composite (full-resolution)
          </figcaption>
        </figure>
      </div>

      <div className="grid grid-cols-4 gap-2 font-data-sm text-[11px]">
        <MiniStat label="Pv" value={candidate.pv.mean} />
        <MiniStat label="CPR" value={candidate.cpr.mean} />
        <MiniStat label="SERD" value={candidate.serd.mean} flag />
        <MiniStat label="T-Ratio" value={candidate.tRatio.mean} />
      </div>
    </div>
  );
}

function MiniStat({ label, value, flag = false }: { label: string; value: number; flag?: boolean }) {
  return (
    <div className="bg-surface-container-low tech-border rounded-sm p-2 text-center">
      <div className="text-outline uppercase text-[10px] tracking-wider">{label}</div>
      <div className={`font-data-md text-data-md font-semibold mono-nums ${flag ? "text-error" : "text-primary"}`}>
        {value.toFixed(3)}
      </div>
    </div>
  );
}
