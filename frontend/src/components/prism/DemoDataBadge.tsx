import type { DataSource } from "@/data/prismDemoData";

export function DemoDataBadge({ source, className = "" }: { source: DataSource; className?: string }) {
  const isReal = source === "real_pipeline";
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded font-data-sm text-[10px] uppercase tracking-wider border ${
        isReal
          ? "bg-secondary-container text-on-secondary-container border-secondary"
          : "bg-surface-container-high text-outline border-outline-variant border-dashed"
      } ${className}`}
      title={
        isReal
          ? "Sourced verbatim from the real PRISM physics pipeline output files"
          : "Fabricated for demo/UI interaction only — not a satellite observation"
      }
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${isReal ? "bg-secondary" : "bg-outline"}`}
        aria-hidden
      />
      {isReal ? "Real Pipeline Data" : "Synthetic Demo"}
    </span>
  );
}
