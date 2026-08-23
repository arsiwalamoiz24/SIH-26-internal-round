/**
 * Shared metric/telemetry-value primitive. Replaces the near-identical
 * Stat / MiniStat / DopStat components previously duplicated across
 * TerrainPanel, RadarVisualizationPanel and DopPanel.
 *
 * Deliberately not a bordered "card" by default -- pass `frame` for the
 * rare case a field needs its own edge (e.g. sitting outside a
 * field-divide group). Most usages should rely on the parent module's
 * .field-divide/.field-divide-h rule instead.
 */
export function Metric({
  label,
  value,
  unit,
  secondary,
  emphasis = "normal",
  tone = "default",
  align = "left",
  frame = false,
}: {
  label: string;
  value: string;
  unit?: string;
  secondary?: string;
  emphasis?: "normal" | "primary" | "large";
  tone?: "default" | "warn" | "critical" | "accent";
  align?: "left" | "center";
  frame?: boolean;
}) {
  const toneClass =
    tone === "warn" ? "text-tertiary" : tone === "critical" ? "text-error" : tone === "accent" ? "text-primary" : "text-on-surface";

  const valueSizeClass =
    emphasis === "large" ? "text-[22px] leading-none" : emphasis === "primary" ? "text-[16px]" : "text-[13px]";

  return (
    <div
      className={`flex flex-col gap-1 ${align === "center" ? "items-center text-center" : "items-start"} ${
        frame ? "p-3 bento-card" : "py-1"
      }`}
    >
      <span className="coord-label">{label}</span>
      <span className={`font-data-md mono-nums font-semibold ${valueSizeClass} ${toneClass}`}>
        {value}
        {unit && <span className="text-[11px] font-normal text-on-surface-variant ml-1">{unit}</span>}
      </span>
      {secondary && <span className="text-[11px] text-on-surface-variant">{secondary}</span>}
    </div>
  );
}
