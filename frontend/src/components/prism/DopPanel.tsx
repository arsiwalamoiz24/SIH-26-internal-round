import type { DopFormulations } from "@/data/prismDemoData";
import { DOP_THRESHOLD_WARNING } from "@/data/prismDemoData";
import { Metric } from "./Metric";

/**
 * Narrower, stat-led companion to RadarVisualizationPanel -- Linear
 * HH/VV is the best-supported formulation and gets the primary
 * readout; Hybrid/Eigenvalue sit as secondary cross-checks.
 */
export function DopPanel({ dop, dopImage, histogramImage }: { dop: DopFormulations; dopImage: string; histogramImage: string }) {
  return (
    <div className="bento-card h-full flex flex-col">
      <div className="bento-header">
        <h3 className="text-[13px] font-semibold text-on-surface tracking-tight m-0">Polarization (DOP)</h3>
      </div>

      <div className="p-4 flex flex-col gap-4 flex-1">
        <Metric
          label="Linear HH/VV (primary)"
          value={dop.linearHhVvMean.toFixed(3)}
          secondary={`median ${dop.linearHhVvMedian.toFixed(3)}`}
          emphasis="large"
          tone="accent"
        />

        <div className="grid grid-cols-2 field-divide -mx-4 px-4 pt-3 border-t border-outline-variant">
          <Metric label="Hybrid LH/LV" value={dop.hybridLhLvMean.toFixed(3)} secondary={`median ${dop.hybridLhLvMedian.toFixed(3)}`} />
          <Metric label="Eigenvalue Purity" value={dop.eigenvaluePurityMean.toFixed(3)} />
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div className="viewport-frame">
            <img src={dopImage} alt="Candidate DOP map" className="w-full h-28 object-cover" />
          </div>
          <div className="viewport-frame">
            <img src={histogramImage} alt="Candidate DOP histogram" className="w-full h-28 object-cover" />
          </div>
        </div>

        <div className="coord-label">
          {dop.validPixels.toLocaleString("en-US")} valid px · {dop.pctNan.toFixed(1)}% NaN
        </div>

        <p className="text-[11px] text-on-surface-variant leading-relaxed m-0 pt-3 border-t border-outline-variant">
          {DOP_THRESHOLD_WARNING}
        </p>
      </div>
    </div>
  );
}
