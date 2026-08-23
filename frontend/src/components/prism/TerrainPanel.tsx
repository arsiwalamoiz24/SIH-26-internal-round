import type { TerrainStats } from "@/data/prismDemoData";
import { TERRAIN_THRESHOLD_LABEL } from "@/data/prismDemoData";
import { Metric } from "./Metric";

/**
 * Asymmetric image/stat merge -- the terrain composite bleeds across
 * most of the module width, stats sit alongside as a narrow column
 * rather than the image being squeezed into a uniform thumbnail slot.
 * Mostly borderless: only the image gets a thin viewport frame.
 */
export function TerrainPanel({ terrain, terrainImage }: { terrain: TerrainStats; terrainImage: string }) {
  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-[13px] font-semibold text-on-surface tracking-tight m-0">Terrain</h3>
        <span className="coord-label">{terrain.hazardThresholdDeg}° hazard threshold — {TERRAIN_THRESHOLD_LABEL}</span>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_260px] gap-4 items-stretch">
        <div className="viewport-frame">
          <img src={terrainImage} alt="PSR terrain composite" className="w-full h-[280px] object-cover" />
        </div>
        <div className="flex flex-col justify-center gap-4 field-divide-h">
          <Metric label="Mean PSR Slope" value={terrain.meanSlopeDeg.toFixed(1)} unit="°" emphasis="large" />
          <div className="pt-4">
            <Metric
              label={`Slope > ${terrain.hazardThresholdDeg}°`}
              value={terrain.pctExceedsHazardThreshold.toFixed(1)}
              unit="%"
              tone="warn"
              emphasis="primary"
            />
          </div>
          <div className="pt-4">
            <Metric label="Terrain Ruggedness Index" value={terrain.triMeters.toFixed(1)} unit="m" emphasis="primary" />
          </div>
        </div>
      </div>
    </div>
  );
}
