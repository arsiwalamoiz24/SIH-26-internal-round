"use client";

import { SYNTHETIC_TIMESERIES, SYNTHETIC_TIMESERIES_LABEL } from "@/data/prismDemoData";
import { DemoDataBadge } from "./DemoDataBadge";

const SERIES: Array<{ key: "pv" | "cpr" | "serd" | "t_ratio"; label: string; color: string }> = [
  { key: "pv", label: "Pv", color: "var(--color-primary)" },
  { key: "cpr", label: "CPR", color: "var(--color-secondary)" },
  { key: "serd", label: "SERD", color: "var(--color-error)" },
  { key: "t_ratio", label: "T-Ratio", color: "var(--color-tertiary)" },
];

const W = 560;
const H = 160;
const PAD = 24;

export function CandidateTimeSeriesChart() {
  const points = SYNTHETIC_TIMESERIES;
  const values = points.flatMap((p) => [p.pv, p.cpr, p.serd, p.t_ratio]);
  const min = Math.min(...values) - 0.03;
  const max = Math.max(...values) + 0.03;

  const xFor = (i: number) => PAD + (i / (points.length - 1)) * (W - PAD * 2);
  const yFor = (v: number) => H - PAD - ((v - min) / (max - min)) * (H - PAD * 2);

  return (
    <div className="bg-surface-container-lowest tech-border rounded p-4 flex flex-col gap-2">
      <div className="flex items-center justify-between pb-2 tech-border-b">
        <h3 className="font-h2 text-h2 text-on-surface uppercase tracking-tight m-0">
          Historical Trend (Demo)
        </h3>
        <DemoDataBadge source="synthetic_demo" />
      </div>

      <div className="bg-tertiary-container/10 border border-tertiary-container/40 rounded px-2 py-1 font-data-sm text-[10px] text-tertiary uppercase tracking-wider text-center">
        {SYNTHETIC_TIMESERIES_LABEL}
      </div>

      <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto">
        {[0, 0.25, 0.5, 0.75, 1].map((f) => (
          <line
            key={f}
            x1={PAD}
            x2={W - PAD}
            y1={PAD + f * (H - PAD * 2)}
            y2={PAD + f * (H - PAD * 2)}
            stroke="var(--color-outline-variant)"
            strokeWidth={1}
          />
        ))}
        {SERIES.map((s) => (
          <polyline
            key={s.key}
            fill="none"
            stroke={s.color}
            strokeWidth={2}
            points={points.map((p, i) => `${xFor(i)},${yFor(p[s.key])}`).join(" ")}
          />
        ))}
        {points.map((p, i) => (
          <text
            key={p.date}
            x={xFor(i)}
            y={H - 4}
            fontSize={8}
            textAnchor="middle"
            fill="var(--color-outline)"
            fontFamily="monospace"
          >
            {i % 2 === 0 ? p.date : ""}
          </text>
        ))}
      </svg>

      <div className="flex gap-3 justify-center font-data-sm text-[10px] text-on-surface-variant">
        {SERIES.map((s) => (
          <span key={s.key} className="flex items-center gap-1">
            <span className="w-2 h-0.5" style={{ backgroundColor: s.color }} />
            {s.label}
          </span>
        ))}
      </div>
    </div>
  );
}
