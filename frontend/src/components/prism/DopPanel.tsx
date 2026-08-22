import type { DopFormulations } from "@/data/prismDemoData";
import { DOP_THRESHOLD_WARNING } from "@/data/prismDemoData";
import { DemoDataBadge } from "./DemoDataBadge";

export function DopPanel({ dop, dopImage, histogramImage }: { dop: DopFormulations; dopImage: string; histogramImage: string }) {
  return (
    <div className="bg-surface-container-lowest tech-border rounded p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between pb-2 tech-border-b">
        <h3 className="font-h2 text-h2 text-on-surface uppercase tracking-tight m-0">
          Degree of Polarization (DOP)
        </h3>
        <DemoDataBadge source={dop.source} />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-sm overflow-hidden tech-border">
          <img src={dopImage} alt="Candidate DOP map" className="w-full h-40 object-cover" />
        </div>
        <div className="rounded-sm overflow-hidden tech-border">
          <img src={histogramImage} alt="Candidate DOP histogram" className="w-full h-40 object-cover" />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2">
        <DopStat
          label="Linear HH/VV"
          primary
          mean={dop.linearHhVvMean}
          median={dop.linearHhVvMedian}
        />
        <DopStat label="Hybrid LH/LV" mean={dop.hybridLhLvMean} median={dop.hybridLhLvMedian} />
        <DopStat label="Eigenvalue Purity" mean={dop.eigenvaluePurityMean} />
      </div>

      <div className="font-data-sm text-[11px] text-on-surface-variant">
        {dop.validPixels.toLocaleString("en-US")} valid pixels · {dop.pctNan.toFixed(1)}% NaN
      </div>

      <div className="bg-tertiary-container/10 border border-tertiary-container/40 rounded p-2 flex gap-2">
        <span className="material-symbols-outlined text-tertiary text-[16px] shrink-0">warning</span>
        <p className="font-body-sm text-[11px] text-on-surface-variant m-0">{DOP_THRESHOLD_WARNING}</p>
      </div>
    </div>
  );
}

function DopStat({
  label,
  mean,
  median,
  primary = false,
}: {
  label: string;
  mean: number;
  median?: number;
  primary?: boolean;
}) {
  return (
    <div
      className={`rounded-sm p-2 flex flex-col gap-0.5 ${
        primary ? "bg-primary-container/10 border border-primary" : "bg-surface-container-low tech-border"
      }`}
    >
      <div className="font-data-sm text-[10px] uppercase tracking-wider text-outline flex items-center gap-1">
        {label}
        {primary && (
          <span className="text-primary font-semibold text-[9px] normal-case">primary</span>
        )}
      </div>
      <div className="text-data-md font-data-md text-on-surface font-semibold mono-nums">
        {mean.toFixed(3)}
      </div>
      {median !== undefined && (
        <div className="font-data-sm text-[10px] text-on-surface-variant">
          median <span className="mono-nums">{median.toFixed(3)}</span>
        </div>
      )}
    </div>
  );
}
