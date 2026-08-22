import type { TerrainStats } from "@/data/prismDemoData";
import { TERRAIN_THRESHOLD_LABEL } from "@/data/prismDemoData";
import { DemoDataBadge } from "./DemoDataBadge";

export function TerrainPanel({ terrain, terrainImage }: { terrain: TerrainStats; terrainImage: string }) {
  return (
    <div className="bg-surface-container-lowest tech-border rounded p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between pb-2 tech-border-b">
        <h3 className="font-h2 text-h2 text-on-surface uppercase tracking-tight m-0">Terrain</h3>
        <DemoDataBadge source={terrain.source} />
      </div>

      <div className="rounded-sm overflow-hidden tech-border">
        <img src={terrainImage} alt="PSR terrain composite" className="w-full h-44 object-cover" />
      </div>

      <div className="grid grid-cols-3 gap-2">
        <Stat label="Mean PSR Slope" value={`${terrain.meanSlopeDeg.toFixed(1)}°`} />
        <Stat
          label={`Slope > ${terrain.hazardThresholdDeg}°`}
          value={`${terrain.pctExceedsHazardThreshold.toFixed(1)}%`}
          warn
        />
        <Stat label="TRI" value={`${terrain.triMeters.toFixed(1)} m`} />
      </div>

      <div className="font-data-sm text-[10px] text-outline uppercase tracking-wider">
        {terrain.hazardThresholdDeg}° hazard threshold: {TERRAIN_THRESHOLD_LABEL}
      </div>
    </div>
  );
}

function Stat({ label, value, warn = false }: { label: string; value: string; warn?: boolean }) {
  return (
    <div className="bg-surface-container-low tech-border rounded-sm p-2 text-center">
      <div className="font-data-sm text-[10px] uppercase tracking-wider text-outline">{label}</div>
      <div
        className={`text-data-md font-data-md font-semibold mono-nums mt-0.5 ${
          warn ? "text-tertiary" : "text-on-surface"
        }`}
      >
        {value}
      </div>
    </div>
  );
}
