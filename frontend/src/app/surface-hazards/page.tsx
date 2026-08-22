// app/surface-hazards/page.tsx
"use client";

import { useState } from "react";
import { getTargetCrater, getTerrainStats } from "@/lib/api";
import { IllustrativeBanner } from "@/components/prism/IllustrativeBanner";
import "material-symbols";

type Basemap = "optical" | "elevation" | "slope" | "geology";

const BASEMAPS: { id: Basemap; label: string }[] = [
  { id: "optical", label: "OPTICAL CONTEXT" },
  { id: "elevation", label: "ELEVATION (REAL)" },
  { id: "slope", label: "RADAR ROUGHNESS" },
  { id: "geology", label: "GEOLOGY (REF)" },
];

const COMPOSITION = [
  { label: "HIGHLAND REGOLITH", pct: 68, color: "bg-primary" },
  { label: "BLOCKY EJECTA", pct: 18, color: "bg-[#64748b]" },
  { label: "CRATER BASIN MAT.", pct: 9, color: "bg-[#94a3b8]" },
  { label: "BEDROCK FACETS", pct: 5, color: "bg-[#475569]" },
];

const GEO_UNITS = [
  { label: "POLAR REGOLITH FACIES", pct: "48%", color: "bg-[#d97706]" },
  { label: "IMPACT MELT DEPOSITS", pct: "26%", color: "bg-[#0ea5e9]" },
  { label: "HIGH-ALBEDO RIM BLOCKS", pct: "16%", color: "bg-[#4f46e5]" },
  { label: "FRACTURED CRATER FLOOR", pct: "10%", color: "bg-[#8b5cf6]" },
];

const ILLUMINATION = [
  { label: "ILLUMINATION", value: "35%" },
  { label: "SUN ANGLE", value: "11.2°" },
  { label: "SUNLIGHT WINDOW", value: "4.8 h/d" },
  { label: "SHADOW COVERAGE", value: "65%" },
];

const FEATURES = [
  { name: "Target PSR Interior", type: "Shadowed Basin", elev: "-2.1 km", size: "14.2 km²", conf: 93 },
  { name: "North Rim Plateau", type: "Landing Zone Alpha", elev: "+0.2 km", size: "2.4 km", conf: 96 },
  { name: "East Ridge Crest", type: "Elevated Rim", elev: "+0.4 km", size: "3.1 km", conf: 88 },
  { name: "South Approach Ramp", type: "Incline Corridor", elev: "-0.8 km", size: "1.8 km", conf: 82 },
  { name: "West Lowland Plain", type: "Safe Regolith", elev: "-1.5 km", size: "4.2 km", conf: 98 },
];

const SOURCES = [
  { icon: "satellite", label: "Chandrayaan-2 DFSAR L-Band (real pipeline output)" },
  { icon: "layers", label: "NASA LOLA PSR Survey (real terrain source)" },
  { icon: "public", label: "Optical Context — Reference Basemap (illustrative, not live imagery)" },
  { icon: "memory", label: "PRISM Radar Roughness & Likelihood Model (illustrative)" },
];

// Illustrative demo log — timestamps and events are staged for UI walkthroughs, not a real
// telemetry/processing feed.
const LOGS = [
  { t: "T+00:04:32", tone: "ok", msg: "DFSAR L-band full-res window (265x253) loaded" },
  { t: "T+00:03:15", tone: "info", msg: "Yamaguchi Y4R decomposition layers validated" },
  { t: "T+00:02:48", tone: "ok", msg: "Volume scattering anomaly ΔPv = +0.081 isolated" },
  { t: "T+00:01:42", tone: "info", msg: "Optical context reference registered to SP_840980" },
  { t: "T+00:01:18", tone: "ok", msg: "LOLA PSR polygon boundary synchronized" },
  { t: "T+00:00:52", tone: "ok", msg: "LOLA 20m/px DEM slope/elevation/TRI computed (Track G)" },
  { t: "T+00:00:11", tone: "info", msg: "PSR-interior hazard flagged: 78.6% exceeds 20° threshold" },
];

const MAP_LABELS = [
  { top: "30%", left: "38%", live: true, text: "SITE ALPHA (NORTH RIM)" },
  { top: "52%", left: "50%", live: true, text: "PEAK ICE ANOMALY (PSR)" },
  { top: "25%", left: "68%", live: false, text: "EAST RIDGE" },
  { top: "72%", left: "46%", live: false, text: "SOUTH INCLINE" },
  { top: "45%", left: "18%", live: false, text: "WEST PLAIN" },
];

const MAP_MARKERS = [
  { top: "28%", left: "37%", live: true },
  { top: "50%", left: "49%", live: true },
  { top: "24%", left: "67%", live: false },
];

const MAP_TOOLS = [
  { icon: "add", title: "Zoom In" },
  { icon: "remove", title: "Zoom Out" },
  { icon: "my_location", title: "Center Map" },
  { icon: "straighten", title: "Measure Distance" },
  { icon: "layers", title: "Layers" },
  { icon: "grid_on", title: "Toggle Grid" },
];

const MAP_SRC =
  "https://lh3.googleusercontent.com/aida-public/AB6AXuBzBBEp4HWSP79melqIx1wQBFOqiWjRuXOtLrabMHxVfqVB5a_okUsvaQlL_CoTLnJj41ZRjIGBv3csbMyzNfHFxtYnMyZU5ERBgYM-JqOFYNOL5VrlhDYaEmh0Ua1uGpfSNwUmNJGJUXct5GGEDzivsvYB4nyWomjxX81MZaQj4U5YQ3H6iiKy5oLgdS9GjJDz4so1Dhf7zMgs-4BxdpmKV0hw3WgwgcrpxSpK_uzuFQBjWQL-dfNe";

export default function SurfaceMap() {
  const target = getTargetCrater();
  const terrain = getTerrainStats();
  const [basemap, setBasemap] = useState<Basemap>("optical");
  const [selected, setSelected] = useState(FEATURES[0].name);
  const [showGrid, setShowGrid] = useState(true);

  const LOCATION = {
    lat: `${Math.abs(target.latitude)}° S`,
    lon: `${target.longitude}° E`,
    targetId: target.psrId,
    radarPvMean: `${target.pvMeanInside} (PSR)`,
    radarPvAnomaly: `+${target.pvAnomaly} (ΔPv)`,
    cprAnomaly: `+${target.cprAnomaly} (CPR)`,
    roughness: `${terrain.roughnessTri.meanTriM.toFixed(2)}m TRI (LOLA)`,
  };

  const TERRAIN_STATS = [
    { label: "MEAN ELEV (LOLA)", value: `${(terrain.elevation.meanM / 1000).toFixed(2)} km` },
    { label: "MEAN SLOPE (LOLA)", value: `${terrain.slope.meanDegWholeWindow.toFixed(1)}°` },
    { label: "PSR INTERIOR SLOPE", value: `${terrain.slope.meanDegPsrInterior.toFixed(1)}°` },
    { label: "ROUGHNESS (TRI)", value: `${terrain.roughnessTri.meanTriM.toFixed(2)} m` },
  ];

  const slopeMaxDeg = 30;
  const SLOPE_BARS = [
    { label: "MIN", deg: 0 },
    { label: "P5", deg: 1.4 },
    { label: "P25", deg: 4.2 },
    { label: "MEDIAN", deg: 8.0 },
    { label: "P75", deg: 15.4 },
    { label: "P95", deg: 26.7 },
  ].map((b) => ({
    h: `${Math.max(4, Math.round((Math.min(b.deg, slopeMaxDeg) / slopeMaxDeg) * 100))}%`,
    color: b.deg < 10 ? "bg-[#10B981]" : b.deg < 20 ? "bg-hazard-warning" : "bg-hazard-critical",
  }));

  const SUMMARY: { label: string; value: string; accent?: boolean; warn?: boolean }[] = [
    { label: "MAPPED AREA", value: `${target.areaKm2} km²` },
    { label: "MEAN ELEVATION", value: `${(terrain.elevation.meanM / 1000).toFixed(2)} km (LOLA)` },
    { label: "AVG. SLOPE", value: `${terrain.slope.meanDegWholeWindow.toFixed(1)}° (LOLA)` },
    { label: "PSR INTERIOR HAZARD", value: `${terrain.slope.pctHazardGte20degPsrInterior.toFixed(1)}%`, warn: true },
    { label: "RADAR AGREEMENT", value: "HIGH (+ΔPv)", accent: true },
  ];

  return (
    <main className="flex-1 flex flex-col overflow-hidden bg-background h-[calc(100vh-80px)]">
      <div className="flex-1 flex overflow-hidden min-h-0">
        {/* Map column */}
        <section className="w-[68%] flex flex-col border-r border-outline-variant bg-surface-container-lowest relative min-h-0">
          <div className="px-4 py-2.5 border-b border-outline-variant bg-surface flex justify-between items-end shrink-0">
            <div>
              <div className="flex items-center gap-2 mb-0.5">
                <h1 className="font-h2 text-h2 text-on-surface m-0">Lunar Surface &amp; Hazard Mapping</h1>
                <span className="bg-amber-50 text-amber-800 border border-amber-300 text-[9px] font-mono font-bold px-1.5 py-0.5 rounded">
                  CONTEXT BASEMAP
                </span>
              </div>
              <p className="font-data-sm text-data-sm text-on-surface-variant tracking-wider uppercase text-[11px]">
                Optical Context (OHRC Pending) • LOLA Slope Reference • DFSAR Radar Anomaly • FR-2
              </p>
              <div className="mt-1.5 max-w-xl">
                <IllustrativeBanner detail="Terrain slope/elevation/roughness (right panel, real LOLA DEM) are pipeline output. Mineralogy, geology units, illumination window, feature confidence scores, and the processing log below are illustrative placeholder content for UI demonstration, not per-candidate pipeline output." />
              </div>
            </div>
            <div className="text-right">
              <div className="flex items-center justify-end gap-2 mb-0.5">
                <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse" />
                <span className="font-data-sm text-data-sm font-bold text-[#10B981] uppercase tracking-wider text-[11px]">
                  Radar Synchronized
                </span>
              </div>
              <p className="font-data-sm text-data-sm text-on-surface-variant text-[10px] font-mono">
                TARGET: {target.psrId} | RES: 2.5 m/px | PROJ: POLAR STEREO
              </p>
            </div>
          </div>

          <div className="flex-1 relative bg-surface-dim overflow-hidden min-h-0">
            <div
              className="absolute inset-0 bg-cover bg-center grayscale"
              style={{ backgroundImage: `url('${MAP_SRC}')` }}
            />
            {showGrid && (
              <>
                <div
                  className="absolute inset-0 pointer-events-none"
                  style={{
                    backgroundImage:
                      "linear-gradient(rgba(200,200,200,0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(200,200,200,0.15) 1px, transparent 1px)",
                    backgroundSize: "100px 100px",
                  }}
                />
                <div
                  className="absolute inset-0 pointer-events-none"
                  style={{
                    backgroundImage:
                      "radial-gradient(circle at center, transparent 0, transparent 99px, rgba(200,200,200,0.1) 100px)",
                    backgroundSize: "200px 200px",
                  }}
                />
              </>
            )}

            <div className="absolute top-20 left-6 bg-surface/95 backdrop-blur-sm border border-outline-variant rounded shadow-sm p-3.5 w-80 z-10 font-mono">
              <div className="font-data-sm text-data-sm text-on-surface-variant uppercase tracking-wider border-b border-outline-variant pb-1.5 mb-2.5 text-[11px] font-bold">
                Selected Location ({target.psrId})
              </div>
              <div className="grid grid-cols-2 gap-y-1.5 text-[11px] mb-3">
                <div className="text-on-surface-variant">LATITUDE</div>
                <div className="font-medium text-right text-on-surface">{LOCATION.lat}</div>
                <div className="text-on-surface-variant">LONGITUDE</div>
                <div className="font-medium text-right text-on-surface">{LOCATION.lon}</div>
                <div className="text-on-surface-variant">RADAR PV MEAN</div>
                <div className="font-medium text-right text-primary font-bold">{LOCATION.radarPvMean}</div>
                <div className="text-on-surface-variant">PV ANOMALY ΔPV</div>
                <div className="font-medium text-right text-[#10b981] font-bold">{LOCATION.radarPvAnomaly}</div>
                <div className="text-on-surface-variant">CPR ANOMALY</div>
                <div className="font-medium text-right text-primary">{LOCATION.cprAnomaly}</div>
                <div className="text-on-surface-variant">RADAR ROUGHNESS</div>
                <div className="font-medium text-right text-on-surface">{LOCATION.roughness}</div>
              </div>
              <div className="text-[9px] text-outline border-t border-outline-variant pt-2 leading-tight">
                Optical Basemap: Reference Context (OHRC Live Co-Registration Pending)
              </div>
            </div>

            <div className="absolute top-6 right-6 flex flex-col gap-2 z-10">
              <div className="bg-surface/95 backdrop-blur-sm border border-outline-variant rounded shadow-sm flex flex-col overflow-hidden">
                {MAP_TOOLS.map((tool, i) => (
                  <button
                    key={tool.icon}
                    type="button"
                    title={tool.title}
                    onClick={() => {
                      if (tool.icon === "grid_on") setShowGrid((v) => !v);
                    }}
                    className={`p-2 hover:bg-surface-variant transition-colors text-on-surface-variant ${
                      i < MAP_TOOLS.length - 1 ? "border-b border-outline-variant" : ""
                    } ${tool.icon === "grid_on" && showGrid ? "bg-surface-container-high text-primary" : ""}`}
                  >
                    <span className="material-symbols-outlined text-[18px]">{tool.icon}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none flex items-center justify-center">
              <div className="w-12 h-12 border-2 border-primary/40 rounded-full" />
              <div className="w-1 h-12 bg-primary/40 absolute" />
              <div className="w-12 h-1 bg-primary/40 absolute" />
              <div className="w-2 h-2 bg-primary rounded-full absolute" />
            </div>

            {MAP_LABELS.map((l) => (
              <div
                key={l.text}
                className="absolute bg-surface/90 backdrop-blur border border-outline-variant px-2 py-1 font-data-sm text-[9px] uppercase tracking-wider rounded pointer-events-none shadow-sm flex items-center gap-1 font-mono"
                style={{ top: l.top, left: l.left }}
              >
                <span
                  className={`rounded-full ${
                    l.live ? "w-1.5 h-1.5 bg-[#10B981]" : "w-1 h-1 bg-on-surface-variant"
                  }`}
                />
                {l.text}
              </div>
            ))}
            <div className="absolute top-[80%] left-[10%] text-on-surface/50 font-data-sm text-xs tracking-[0.2em] pointer-events-none uppercase">
              Western Lowland Plain
            </div>
            <div className="absolute top-[10%] left-[40%] text-on-surface/50 font-data-sm text-xs tracking-[0.2em] pointer-events-none uppercase">
              North Crater Rim Plateau
            </div>
            {MAP_MARKERS.map((m, i) => (
              <div
                key={i}
                className={`absolute rounded-full shadow-[0_0_0_2px_rgba(255,255,255,0.5)] ${
                  m.live ? "w-2 h-2 bg-[#10B981]" : "w-1.5 h-1.5 bg-primary"
                }`}
                style={{ top: m.top, left: m.left }}
              />
            ))}
          </div>

          <div className="h-8 border-t border-outline-variant bg-surface-container-low flex items-center justify-between px-4 shrink-0 font-data-sm text-data-sm text-on-surface-variant text-[11px] font-mono">
            <div className="flex gap-6">
              <span>TARGET CENTER: {Math.abs(target.latitude)}° S / {target.longitude}° E</span>
              <span>ZOOM: 12x</span>
            </div>
            <div className="flex gap-6">
              <span>RADAR RES: 2.5m/px</span>
              <span className="text-[#10B981] font-medium flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#10B981]" />
                DFSAR SYNCED
              </span>
            </div>
          </div>
        </section>

        {/* Analysis column */}
        <section className="w-[32%] bg-surface-container-lowest flex flex-col overflow-y-auto min-h-0">
          <div className="p-3 flex flex-col gap-3">
            <Panel title="Radar Surface &amp; Terrain (Real LOLA DEM)" icon="analytics">
              <div className="grid grid-cols-2 p-3 gap-3">
                {TERRAIN_STATS.map((s) => (
                  <div key={s.label}>
                    <div className="font-data-sm text-data-sm text-on-surface-variant mb-0.5 text-[10px]">
                      {s.label}
                    </div>
                    <div className="font-data-lg text-data-lg text-on-surface text-[14px] font-mono font-semibold">{s.value}</div>
                  </div>
                ))}
              </div>
            </Panel>

            <Panel title="LOLA Slope Distribution (Real, 20m/px)" icon="bar_chart">
              <div className="p-3">
                <div className="flex items-end h-14 gap-1 mb-2 border-b border-outline-variant pb-1">
                  {SLOPE_BARS.map((b, i) => (
                    <div key={i} className={`w-full ${b.color}`} style={{ height: b.h }} />
                  ))}
                </div>
                <div className="flex justify-between font-data-sm text-[9px] text-on-surface-variant mb-2 font-mono">
                  <span>min</span>
                  <span>10° (safe)</span>
                  <span>20°+ (steep)</span>
                  <span>p95</span>
                </div>
                <div className="flex justify-between font-data-sm text-[11px] font-mono flex-wrap gap-y-1">
                  <div>
                    <span className="text-on-surface-variant">MEAN:</span>{" "}
                    <span className="text-on-surface font-semibold">{terrain.slope.meanDegWholeWindow.toFixed(1)}°</span>
                  </div>
                  <div>
                    <span className="text-on-surface-variant">MAX:</span>{" "}
                    <span className="text-on-surface font-semibold">{terrain.slope.maxDegWholeWindow.toFixed(1)}°</span>
                  </div>
                  <div>
                    <span className="text-on-surface-variant">SAFE AREA:</span>{" "}
                    <span className="text-[#10B981] font-bold">{terrain.slope.pctSafeLt10deg.toFixed(1)}%</span>
                  </div>
                </div>
                <div className="mt-2 pt-2 border-t border-outline-variant text-[9px] font-mono text-amber-700 bg-amber-50 -mx-3 -mb-3 px-3 py-2 rounded-b">
                  PSR interior (the actual ice-candidate floor) is steeper: mean {terrain.slope.meanDegPsrInterior.toFixed(1)}°, {terrain.slope.pctHazardGte20degPsrInterior.toFixed(1)}% exceeds the 20° hazard threshold, vs {terrain.slope.pctHazardGte20degApproachTerrain.toFixed(1)}% on the surrounding approach terrain. {terrain.slope.thresholdCaveat}
                </div>
              </div>
            </Panel>

            <Panel title="Highland Mineralogy (Ref Model)" icon="pie_chart">
              <div className="p-3 flex flex-col gap-2 font-data-sm text-xs">
                {COMPOSITION.map((c) => (
                  <div key={c.label} className="flex items-center gap-2">
                    <div className="w-32 text-on-surface-variant truncate text-[11px]">{c.label}</div>
                    <div className="flex-1 h-1.5 bg-surface-variant rounded overflow-hidden">
                      <div className={`h-full ${c.color}`} style={{ width: `${c.pct}%` }} />
                    </div>
                    <div className="w-8 text-right text-on-surface font-mono text-[11px]">{c.pct}%</div>
                  </div>
                ))}
              </div>
            </Panel>

            <Panel title="Solar Illumination Window" icon="light_mode">
              <div className="p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="h-2 flex-1 bg-surface-variant rounded overflow-hidden flex">
                    <div className="h-full bg-[#eab308]" style={{ width: "35%" }} />
                    <div className="h-full bg-on-surface-variant" style={{ width: "65%" }} />
                  </div>
                  <div className="ml-3 font-data-sm text-[9px] font-bold text-[#eab308] border border-[#eab308]/30 px-1.5 py-0.5 rounded uppercase">
                    Partial Illumination
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-y-1.5 font-data-sm text-[11px] font-mono">
                  {ILLUMINATION.map((row) => (
                    <div key={row.label} className="contents">
                      <div className="text-on-surface-variant">{row.label}</div>
                      <div className="text-on-surface text-right font-medium">{row.value}</div>
                    </div>
                  ))}
                </div>
              </div>
            </Panel>
          </div>
        </section>
      </div>

      {/* Lower strip */}
      <section className="h-64 border-t border-outline-variant bg-surface-container-lowest shrink-0 flex flex-col">
        <div className="h-10 border-b border-outline-variant bg-surface-container-low flex divide-x divide-outline-variant">
          {SUMMARY.map((s) => (
            <div key={s.label} className="flex-1 flex flex-col justify-center px-4">
              <div className="font-data-sm text-[9px] text-on-surface-variant uppercase tracking-wider">
                {s.label}
              </div>
              <div
                className={`font-data-sm text-xs font-mono font-semibold ${
                  s.accent ? "text-[#10B981]" : s.warn ? "text-hazard-critical" : "text-on-surface"
                }`}
              >
                {s.value}
              </div>
            </div>
          ))}
        </div>

        <div className="flex-1 flex divide-x divide-outline-variant overflow-hidden">
          <div className="w-1/2 flex flex-col p-3 overflow-hidden">
            <div className="font-data-sm text-data-sm text-on-surface-variant uppercase tracking-wider mb-1.5 text-[11px] font-bold">
              Identified Crater Morphological Units — Illustrative ({target.psrId})
            </div>
            <div className="overflow-y-auto flex-1 border border-outline-variant rounded bg-surface mb-6">
              <table className="w-full text-left border-collapse font-mono text-[11px]">
                <thead className="bg-surface-container-low font-data-sm text-[9px] text-on-surface-variant sticky top-0 border-b border-outline-variant uppercase">
                  <tr>
                    {["Feature", "Classification", "Elevation (Ref)", "Size", "Confidence"].map((h) => (
                      <th key={h} className="p-2 font-normal">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant">
                  {FEATURES.map((f) => (
                    <tr
                      key={f.name}
                      onClick={() => setSelected(f.name)}
                      className={`hover:bg-surface-variant transition-colors cursor-pointer ${
                        selected === f.name ? "bg-surface-container" : ""
                      }`}
                    >
                      <td className="p-1.5 text-on-surface font-medium">{f.name}</td>
                      <td className="p-1.5 text-on-surface-variant">{f.type}</td>
                      <td className="p-1.5 text-on-surface">{f.elev}</td>
                      <td className="p-1.5 text-on-surface-variant">{f.size}</td>
                      <td className={`p-1.5 ${f.conf >= 85 ? "text-[#10B981] font-bold" : "text-amber-600"}`}>
                        {f.conf}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="w-1/4 flex flex-col p-3 overflow-hidden">
            <div className="font-data-sm text-data-sm text-on-surface-variant uppercase tracking-wider mb-1.5 text-[11px] font-bold">
              Data Sources &amp; Provenance
            </div>
            <div className="border border-outline-variant rounded bg-surface h-[125px] p-2.5 flex flex-col gap-1.5 font-data-sm text-[11px] overflow-y-auto font-mono">
              {SOURCES.map((s) => (
                <div
                  key={s.label}
                  className="flex items-center gap-1.5 text-on-surface shrink-0"
                >
                  <span className="material-symbols-outlined text-[13px] text-primary">
                    {s.icon}
                  </span>
                  <span className="truncate">{s.label}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="w-1/4 flex flex-col p-3 overflow-hidden">
            <div className="font-data-sm text-data-sm text-on-surface-variant uppercase tracking-wider mb-1.5 text-[11px] font-bold">
              Scientific Processing Log (Illustrative Demo)
            </div>
            <div className="border border-outline-variant rounded bg-surface h-[125px] p-2 overflow-y-auto font-data-sm text-[10px] font-mono space-y-1">
              {LOGS.map((e) => (
                <div key={e.t} className="flex gap-2">
                  <span className="text-on-surface-variant shrink-0">{e.t}</span>
                  <span className={e.tone === "ok" ? "text-[#10B981]" : "text-[#0ea5e9]"}>
                    •
                  </span>
                  <span className="text-on-surface">{e.msg}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

function Panel({
  title,
  icon,
  children,
}: {
  title: string;
  icon: string;
  children: React.ReactNode;
}) {
  return (
    <div className="border border-outline-variant rounded bg-surface shadow-xs">
      <div className="border-b border-outline-variant px-3 py-1.5 flex justify-between items-center bg-surface-container-low">
        <h3 className="font-data-sm text-data-sm text-on-surface-variant uppercase tracking-wider text-[11px] font-bold">
          {title}
        </h3>
        <span className="material-symbols-outlined text-[15px] text-on-surface-variant">{icon}</span>
      </div>
      {children}
    </div>
  );
}