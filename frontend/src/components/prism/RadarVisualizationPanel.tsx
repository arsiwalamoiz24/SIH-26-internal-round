import type { RealCandidate } from "@/data/prismDemoData";
import { Metric } from "./Metric";

/**
 * Image-led module -- the two radar composites are the actual
 * evidentiary imagery for the candidate, so they get real size
 * (a large primary composite + a smaller secondary one) rather than
 * two equally-cropped thumbnails.
 */
export function RadarVisualizationPanel({ candidate }: { candidate: RealCandidate }) {
  return (
    <div className="bento-card h-full flex flex-col">
      <div className="bento-header">
        <h3 className="text-[13px] font-semibold text-on-surface tracking-tight m-0">Radar Visualization</h3>
        <span className="coord-label">Full-resolution composite</span>
      </div>

      <div className="p-4 flex flex-col gap-3 flex-1">
        <div className="grid grid-cols-[1fr_220px] gap-3 items-start">
          <figure className="m-0 viewport-frame">
            <img
              src={candidate.images.radarMetrics}
              alt="Candidate radar metrics composite"
              className="w-full h-[280px] object-cover"
            />
            <figcaption className="coord-label px-2 py-1.5 border-t border-outline-variant">
              Radar physics composite
            </figcaption>
          </figure>
          <figure className="m-0 viewport-frame">
            <img
              src={candidate.images.overview}
              alt="Candidate overview: Pv, CPR, SERD, boundary and coordinate"
              className="w-full h-[280px] object-cover"
            />
            <figcaption className="coord-label px-2 py-1.5 border-t border-outline-variant">
              Pv / CPR / SERD overview
            </figcaption>
          </figure>
        </div>

        <div className="grid grid-cols-4 field-divide pt-2 border-t border-outline-variant">
          <Metric label="Pv" value={candidate.pv.mean.toFixed(3)} tone="accent" align="center" />
          <Metric label="CPR" value={candidate.cpr.mean.toFixed(3)} tone="accent" align="center" />
          <Metric label="SERD" value={candidate.serd.mean.toFixed(3)} tone="critical" align="center" />
          <Metric label="T-Ratio" value={candidate.tRatio.mean.toFixed(3)} tone="accent" align="center" />
        </div>
      </div>
    </div>
  );
}
