/**
 * PRISM Scientific Data Layer
 * All real values transcribed from PRISM/outputs pipeline files.
 * Source citations inline for every real value.
 */

// ── Seven Candidate PSRs ────────────────────────────────────────
// Source: PRISM/outputs/objective1/evidence_score/physics_evidence_score.json
export const CANDIDATES = [
  {
    id: "SP_840980_0797630",
    label: "SP-840980",
    lat: -84.098,
    lon: 79.764,
    areaKm2: 14.234,
    physicsScore: 1.0,
    rank: 1,
    isPrimary: true,
    deltaPv: 0.0807,
    deltaCpr: 0.0987,
    deltaTratio: 0.1208,
    deltaSerd: -0.0562,
    hazardImage: "/assets/prism/SP_840980_0797630_hazard_map_v2.png",
    shadowcamImage: "/assets/prism/SP_840980_0797630_shadowcam_crop_preview.png",
    shortDescription: "Highest ice-evidence score of 7 candidates. Elevated Pv, CPR and T-Ratio all confirm anomalous backscatter from this permanently shadowed crater interior.",
    terrain: { elevMin: -4410.7, elevMax: -2668.6, elevRange: 1742.1 },
    // Source: PRISM/outputs/objective1/ml/shortlist/shortlist_pixel_anomaly_summary.csv
    // (Track J-v2, independent per-pixel Isolation Forest — Pv/CPR/SERD/T-Ratio bands)
    mlPixel: { meanInside: 0.1938, meanOutside: 0.1771, separation: 0.0166 },
  },
  {
    id: "SP_832640_0090770",
    label: "SP-832640",
    lat: -83.264,
    lon: 9.077,
    areaKm2: 32.494,
    physicsScore: 0.728,
    rank: 2,
    isPrimary: false,
    deltaPv: 0.0244,
    deltaCpr: 0.0560,
    deltaTratio: 0.0433,
    deltaSerd: -0.0209,
    hazardImage: "/assets/prism/shortlist_hazard/SP_832640_0090770_hazard_map.png",
    shadowcamImage: "/assets/prism/shortlist_shadowcam/SP_832640_0090770_M013535360SE_preview.png",
    terrainImage: "/assets/prism/shortlist_terrain/SP_832640_0090770_terrain_composite.png",
    radarImage: "/assets/prism/shortlist_radar/SP_832640_0090770_radar_composite.png",
    shortDescription: "Second-ranked candidate. Moderate positive CPR and Pv anomalies. Larger area than primary.",
    terrain: { elevMin: -4200, elevMax: -2400, elevRange: 1800 },
    mlPixel: { meanInside: 0.1834, meanOutside: 0.1739, separation: 0.0095 },
  },
  {
    id: "SP_809570_2454450",
    label: "SP-809570",
    lat: -80.957,
    lon: 245.445,
    areaKm2: 9.198,
    physicsScore: 0.696,
    rank: 3,
    isPrimary: false,
    deltaPv: 0.0489,
    deltaCpr: -0.0100,
    deltaTratio: 0.0432,
    deltaSerd: -0.0034,
    hazardImage: "/assets/prism/shortlist_hazard/SP_809570_2454450_hazard_map.png",
    shadowcamImage: "/assets/prism/shortlist_shadowcam/SP_809570_2454450_M016666798SE_preview.png",
    terrainImage: "/assets/prism/shortlist_terrain/SP_809570_2454450_terrain_composite.png",
    radarImage: "/assets/prism/shortlist_radar/SP_809570_2454450_radar_composite.png",
    shortDescription: "Positive Pv and T-Ratio anomaly. Mixed CPR reading. Smaller crater at more accessible latitude.",
    terrain: { elevMin: -4100, elevMax: -2500, elevRange: 1600 },
    mlPixel: { meanInside: 0.2166, meanOutside: 0.1559, separation: 0.0607 },
  },
  {
    id: "SP_819860_1568660",
    label: "SP-819860",
    lat: -81.986,
    lon: 156.866,
    areaKm2: 10.735,
    physicsScore: 0.613,
    rank: 4,
    isPrimary: false,
    deltaPv: 0.0065,
    deltaCpr: 0.0247,
    deltaTratio: 0.0136,
    deltaSerd: 0.0030,
    hazardImage: "/assets/prism/shortlist_hazard/SP_819860_1568660_hazard_map.png",
    shadowcamImage: "/assets/prism/shortlist_shadowcam/SP_819860_1568660_M019650752SE_preview.png",
    terrainImage: "/assets/prism/shortlist_terrain/SP_819860_1568660_terrain_composite.png",
    radarImage: "/assets/prism/shortlist_radar/SP_819860_1568660_radar_composite.png",
    shortDescription: "Moderate signals across all four radar metrics. SERD anomaly slightly positive unlike most candidates.",
    terrain: { elevMin: -3900, elevMax: -2300, elevRange: 1600 },
    mlPixel: { meanInside: 0.2801, meanOutside: 0.1826, separation: 0.0975 },
  },
  {
    id: "SP_842420_0421060",
    label: "SP-842420",
    lat: -84.242,
    lon: 42.106,
    areaKm2: 25.463,
    physicsScore: 0.522,
    rank: 5,
    isPrimary: false,
    deltaPv: 0.0160,
    deltaCpr: -0.0161,
    deltaTratio: -0.0365,
    deltaSerd: -0.0033,
    hazardImage: "/assets/prism/shortlist_hazard/SP_842420_0421060_hazard_map.png",
    shadowcamImage: "/assets/prism/shortlist_shadowcam/SP_842420_0421060_M018010390SE_preview.png",
    terrainImage: "/assets/prism/shortlist_terrain/SP_842420_0421060_terrain_composite.png",
    radarImage: "/assets/prism/shortlist_radar/SP_842420_0421060_radar_composite.png",
    shortDescription: "Mixed evidence. Slight positive Pv offset but negative CPR and T-Ratio anomalies.",
    terrain: { elevMin: -4500, elevMax: -2600, elevRange: 1900 },
    mlPixel: { meanInside: 0.1892, meanOutside: 0.1962, separation: -0.0069 },
  },
  {
    id: "SP_817950_1586580",
    label: "SP-817950",
    lat: -81.795,
    lon: 158.658,
    areaKm2: 43.429,
    physicsScore: 0.293,
    rank: 6,
    isPrimary: false,
    deltaPv: -0.0212,
    deltaCpr: -0.0804,
    deltaTratio: -0.0897,
    deltaSerd: 0.0287,
    hazardImage: "/assets/prism/shortlist_hazard/SP_817950_1586580_hazard_map.png",
    shadowcamImage: "/assets/prism/shortlist_shadowcam/SP_817950_1586580_M017274985SE_preview.png",
    terrainImage: "/assets/prism/shortlist_terrain/SP_817950_1586580_terrain_composite.png",
    radarImage: "/assets/prism/shortlist_radar/SP_817950_1586580_radar_composite.png",
    shortDescription: "Negative CPR and T-Ratio deltas. Largest candidate by area. Lowest evidence among shortlisted set.",
    terrain: { elevMin: -4800, elevMax: -2200, elevRange: 2600 },
    mlPixel: { meanInside: 0.1726, meanOutside: 0.1874, separation: -0.0148 },
  },
  {
    id: "SP_830080_0535120",
    label: "SP-830080",
    lat: -83.008,
    lon: 53.512,
    areaKm2: 22.471,
    physicsScore: 0.0,
    rank: 7,
    isPrimary: false,
    deltaPv: -0.0682,
    deltaCpr: -0.1551,
    deltaTratio: -0.1674,
    deltaSerd: 0.0400,
    hazardImage: "/assets/prism/shortlist_hazard/SP_830080_0535120_hazard_map.png",
    shadowcamImage: "/assets/prism/shortlist_shadowcam/SP_830080_0535120_M074536836SE_preview.png",
    terrainImage: "/assets/prism/shortlist_terrain/SP_830080_0535120_terrain_composite.png",
    radarImage: "/assets/prism/shortlist_radar/SP_830080_0535120_radar_composite.png",
    shortDescription: "Below baseline on all three scored metrics. Anchors the lower bound of the shortlist ranking.",
    terrain: { elevMin: -4300, elevMax: -2500, elevRange: 1800 },
    mlPixel: { meanInside: 0.2097, meanOutside: 0.1973, separation: 0.0124 },
  },
] as const;

// ── SP-ID label helper ───────────────────────────────────────────
// The 7 screened candidates use "SP-XXXXXX" (derived from the PSR_ID's
// first coordinate group). Faustini/Cabeus use the same derivation so their
// dropdown/list entries read consistently, e.g. "SP-871460 Faustini".
export function spIdLabel(id: string): string {
  const parts = id.split("_");
  return `SP-${parts[1] ?? id}`;
}

// ── Primary Candidate — Full Data ───────────────────────────────
// Source: physics_evidence_score.json, terrain_stats.json, candidate_physics_summary.json
export const PRIMARY = {
  id: "SP_840980_0797630",
  lat: -84.098,
  lon: 79.764,
  latStr: "84.098° S",
  lonStr: "79.764° E",
  areaKm2: 14.234,

  // Radar metrics — source: candidate_physics_summary.json
  radar: {
    pv:     { mean: 0.4543, median: 0.4692, percentile: 93.9,  delta: 0.0807 },
    cpr:    { mean: 0.5650, median: 0.5425, percentile: 97.2,  delta: 0.0987 },
    serd:   { mean: 0.6729, median: 0.6690, percentile: 4.3,   delta: -0.0562 }, // ANOMALOUS — low percentile
    tRatio: { mean: 0.5710, median: 0.5693, percentile: 95.8,  delta: 0.1208 },
  },

  // Terrain — source: SP_840980_0797630_terrain_stats.json
  terrain: {
    elevMin: -4410.7,
    elevMax: -2668.6,
    elevRange: 1742.1,
    meanSlopeDeg: 10.72,
    psrMeanSlopeDeg: 22.08,
    pctHazardGte20Deg: 20.18,
    psrPctHazardGte20Deg: 78.63,
    approachPctHazard: 10.48,
    roughnessTRI: 6.293,
    approachRoughnessTRI: 2.471,
    illuminationFrac: 0.0017, // permanently shadowed
  },

  // Hazard — source: SP_840980_0797630_hazard_map_v2.json
  hazard: {
    pctSafe: 0.38,
    pctCaution: 95.37,
    pctHazard: 4.25,
    psrPctHazardGte066: 8.0,
    meanHazardInside: 0.597,
    meanHazardOutside: 0.435,
  },

  // ML — source: isolation_forest_results.json
  ml: {
    method: "Isolation Forest",
    nPSRs: 336,
    rank: 40,
    isAnomaly: true,
    anomalyScore: 0.0056,
  },

  // Evidence score — source: physics_evidence_score.json
  evidence: {
    score: 1.0,
    rank: 1,
    outOf: 7,
  },

  // Acquisition — source: candidate_acquisition.json
  acquisition: {
    id: "ch2_sar_ncxl_20220318t130441232_d_fp_d18",
    date: "2022-03-18",
    instrument: "Chandrayaan-2 DFSAR",
    band: "L-band",
    mode: "Full-polarimetric",
    station: "d18",
  },

  // Images
  images: {
    radar: "/assets/prism/SP_840980_0797630_radar_composite.png",
    terrain: "/assets/prism/SP_840980_0797630_terrain_composite.png",
    hazard: "/assets/prism/SP_840980_0797630_hazard_map_v2.png",
    shadowcam: "/assets/prism/SP_840980_0797630_shadowcam_crop_preview.png",
    boulderDetection: "/assets/prism/SP_840980_boulder_detection.png",
    zerodce: "/assets/prism/SP_840980_zerodce.png",
    pv: "/assets/prism/candidate_pv.png",
    cpr: "/assets/prism/candidate_cpr.png",
    serd: "/assets/prism/candidate_serd.png",
    tratio: "/assets/prism/candidate_tratio.png",
    locator: "/assets/prism/candidate_locator.png",
    dopHistogram: "/assets/prism/candidate_dop_histogram.png",
    regionOverview: "/assets/prism/regional_hazard_overview.png",
    quickmap: "/assets/prism/quickmap_2_candidate_crop_marked.png",
    // Real hazard composite (square, matches the traverse map's 1:1 overlay box) —
    // was a generic stock illustration (path.png), replaced with real PRISM data.
    path: "/assets/prism/SP_840980_0797630_hazard_map_v2.png",
  },
  
  // Traverse
  traverse: {
    distance: "1.2 km",
    estTime: "4.5 hrs",
    maxSlope: "18.2°",
    waypoints: [
      { id: "WP-Alpha", x: 15, y: 15, type: "Entry Point", slope: "4.5°", hazard: "Low", boulders: 0 },
      { id: "WP-Beta", x: 40, y: 35, type: "Nav Node", slope: "12.1°", hazard: "Medium", boulders: 3 },
      { id: "WP-Gamma", x: 70, y: 65, type: "Hazard Zone", slope: "18.2°", hazard: "High", boulders: 12 },
      { id: "WP-Delta", x: 85, y: 85, type: "Ice Target", slope: "8.4°", hazard: "Low", boulders: 1 },
    ],
  },
} as const;

// ── Faustini reference/validation case ──────────────────────────
// Faustini is NOT one of PRISM's 7 screened candidates — it's a published,
// externally-confirmed ice-evidence site (Sinha et al. 2026, npj Space
// Exploration) used here as a validation case: can PRISM's own methodology
// detect already-known ice evidence when we know where to look?
// Source: PRISM/outputs/objective1/{SP_871460_0840750,faustini_*}.json,
// PRISM/docs/DOP_GROUND_TRUTH_INVESTIGATION.md (F2/F3 coordinates & context).
export const FAUSTINI = {
  id: "SP_871460_0840750",
  label: "Faustini",
  lat: -87.146,
  lon: 84.075,
  areaKm2: 663.959,
  overviewRank: 116,
  overviewOutOf: 336,
  isPrimary: false,
  externalEvidence: "M3 (Chandrayaan-1) spectral ice-absorption detection — Li et al. 2018, PNAS",
  // Real LOLA terrain, same window as every other candidate — for the 3D view.
  terrain: { elevMin: -2903.3, elevMax: -2564.4, elevRange: 339.0 },
  // Faustini's real PSR polygon (max radius ~15.8km) is far bigger than the
  // 7 screened candidates' fixed 5000m hazard/terrain crop buffer, so its
  // hazard_only/elevation_only textures were regenerated at this larger real
  // buffer (PRISM/src/regenerate_featured_sites_full_extent.py) instead of
  // being cropped to a small fraction of the actual crater. ShadowCam is a
  // real single-orbital-frame crop (PRISM/src/shadowcam_featured_sites.py,
  // real ASU/im-ldi PDS archive search) -- a much smaller real half-width
  // than the crater itself, unlike hazard/terrain (an orbital swath can't be
  // arbitrarily widened the way a LOLA DEM windowed read can).
  textureHalfM: { hazard: 20500, terrain: 20500, shadowcam: 1500 },
  hazardImage: "/assets/prism/faustini/SP_871460_0840750_hazard_map.png",
  terrainImage: "/assets/prism/faustini/SP_871460_0840750_terrain_composite.png",
  radarImage: "/assets/prism/faustini/SP_871460_0840750_radar_composite.png",
  // Real ShadowCam frame M076693225SE (100% valid pixels, 0.988 adjacent-
  // pixel correlation -- real signal, not sensor noise), found via the same
  // validated ASU/im-ldi PDS search used for the 7 screened candidates.
  shadowcamImage: "/assets/prism/featured_shadowcam/SP_871460_0840750_M076693225SE_preview.png",

  // Whole-PSR real Pv/CPR/SERD/T-Ratio, same methodology as the 7 screened
  // candidates — averaged across the ENTIRE 664 km^2 crater, most of which
  // is not the small ice-bearing sub-region.
  wholePsr: {
    pv:  { inside: 0.2983, outside: 0.3201, delta: -0.0218 },
    cpr: { inside: 0.3081, outside: 0.3374, delta: -0.0293 },
    srd: { inside: 0.7824, outside: 0.7660, delta: 0.0164 },  // wrong sign vs. ice-anomalous direction
    trt: { inside: 0.3185, outside: 0.3515, delta: -0.0330 },
  },

  // F2 and F3: the exact 1100m/700m doubly-shadowed sub-craters Sinha et al.
  // 2026 report ice evidence for, analyzed with the same real Y4R/CPR mosaic
  // and inside/outside methodology, just at the correct (much smaller) scale.
  subcraters: [
    {
      id: "F2", lat: -87.39, lon: 82.31, diameterM: 1100,
      pv:  { inside: 0.6358, outside: 0.5846, delta: 0.0512 },
      cpr: { inside: 0.9654, outside: 0.8091, delta: 0.1563 },
      srd: { inside: 0.5277, outside: 0.5543, delta: -0.0266 },
      trt: { inside: 0.9976, outside: 0.8221, delta: 0.1755 },
      image: "/assets/prism/faustini/faustini_F2_pv_cpr.png",
    },
    {
      id: "F3", lat: -87.31, lon: 86.333, diameterM: 700,
      pv:  { inside: 0.6208, outside: 0.4749, delta: 0.1459 },
      cpr: { inside: 0.8823, outside: 0.5683, delta: 0.3140 },
      srd: { inside: 0.5214, outside: 0.6422, delta: -0.1208 },
      trt: { inside: 0.9174, outside: 0.5914, delta: 0.3261 },
      image: "/assets/prism/faustini/faustini_F3_pv_cpr.png",
    },
  ],

  images: {
    radar: "/assets/prism/faustini/SP_871460_0840750_radar_composite.png",
    hazard: "/assets/prism/faustini/SP_871460_0840750_hazard_map.png",
    terrain: "/assets/prism/faustini/SP_871460_0840750_terrain_composite.png",
  },
} as const;

// ── Cabeus reference case ────────────────────────────────────────
// Cabeus hosts the LCROSS impact site — the only place on the Moon with a
// direct, in-situ physical measurement of water (Colaprete et al. 2010,
// Science: 5.6±2.9 wt% in the impact ejecta plume) — not a remote inference.
// Featured here on that real, external, undisputed fact. PRISM's own DFSAR
// radar signature at Cabeus (same instrument/methodology as the 7 screened
// candidates, both whole-PSR and targeted at the exact LCROSS coordinate)
// does not itself show an anomalous reading — reported honestly below,
// rather than asserting a radar finding PRISM's own pipeline didn't make.
// Source: PRISM/outputs/objective1/{SP_844580_3134320,cabeus_targeted_pv_cpr}.json.
export const CABEUS = {
  id: "SP_844580_3134320",
  label: "Cabeus",
  lat: -84.6796,
  lon: -48.7093,
  areaKm2: 315.029,
  isPrimary: false,
  externalEvidence: "LCROSS direct impact-plume water detection — 5.6±2.9 wt%, Colaprete et al. 2010, Science",
  // Wide-window (9km) real LOLA stats, centered on the PSR's own true polygon
  // centroid (not the LCROSS point — see terrain/page.tsx CraterMesh comment).
  terrain: { elevMin: -3839.2, elevMax: -1074.2, elevRange: 2765.0 },
  // Same fix as Faustini's textureHalfM — Cabeus's real PSR polygon (max
  // radius ~15.9km) needed its own regenerated, properly-sized hazard/
  // terrain crop buffer instead of the 7 candidates' fixed 5000m default.
  // ShadowCam is a real single-orbital-frame crop, same real constraint as
  // Faustini's (see its comment above).
  textureHalfM: { hazard: 20700, terrain: 20700, shadowcam: 1500 },
  hazardImage: "/assets/prism/cabeus/SP_844580_3134320_hazard_map.png",
  terrainImage: "/assets/prism/cabeus/SP_844580_3134320_terrain_composite.png",
  radarImage: "/assets/prism/cabeus/SP_844580_3134320_radar_composite.png",
  // Real ShadowCam frame M077619504SE (85.5% valid pixels, 0.938 adjacent-
  // pixel correlation), same real ASU/im-ldi PDS archive search as the 7
  // screened candidates and Faustini.
  shadowcamImage: "/assets/prism/featured_shadowcam/SP_844580_3134320_M077619504SE_preview.png",

  // Whole-PSR real Pv/CPR/SERD/T-Ratio, same DFSAR instrument/methodology as
  // the 7 screened candidates and Faustini.
  wholePsr: {
    pv:  { inside: 0.1719, outside: 0.2037, delta: -0.0318 },
    cpr: { inside: 0.1457, outside: 0.1825, delta: -0.0368 },
    srd: { inside: 0.8800, outside: 0.8564, delta: 0.0236 },
    trt: { inside: 0.1567, outside: 0.1982, delta: -0.0415 },
  },

  // Targeted at the exact LCROSS impact coordinate (Marshall et al. 2011),
  // 2km window — the same "zoom to the exact published point" methodology
  // used for Faustini's F2/F3, applied here for a fair comparison.
  targeted: {
    label: "Exact LCROSS impact point",
    pv:  { inside: 0.2138, outside: 0.2483, delta: -0.0345 },
    cpr: { inside: 0.1610, outside: 0.2134, delta: -0.0524 },
    srd: { inside: 0.8522, outside: 0.8238, delta: 0.0284 },
    trt: { inside: 0.1942, outside: 0.2553, delta: -0.0611 },
    image: "/assets/prism/cabeus/cabeus_lcross_pv_cpr.png",
    note: "A separate real Mini-RF (S-band) analysis at this exact coordinate found an elevated CPR>1 pixel fraction — traced to a documented fresh-crater ejecta ray (Fassett et al. 2024), a real non-ice mechanism, not this DFSAR (L-band) result.",
  },
} as const;

// ── Unified site directory ───────────────────────────────────────
// A single flat list of all 9 sites (Faustini + Cabeus first, then the 7
// screened candidates in rank order) for dropdowns and map markers. Faustini
// and Cabeus are real, externally-validated reference sites — not a
// separate "featured" subsection, just two more rows in the same list, each
// labeled the same "SP-XXXXXX Name" way as the 7 candidates.
export type SiteDirectoryEntry = {
  id: string;
  dropdownLabel: string; // "SP-871460 Faustini" / "SP-840980 (Primary)"
  shortLabel: string;    // "Faustini" / "SP-840980"
  lat: number;
  lon: number;
  isPrimary: boolean;
  isFeatured: boolean;   // Faustini/Cabeus: real external validation sites, not PRISM-screened
};

export const ALL_SITES: SiteDirectoryEntry[] = [
  {
    id: FAUSTINI.id, dropdownLabel: `${spIdLabel(FAUSTINI.id)} Faustini`, shortLabel: FAUSTINI.label,
    lat: FAUSTINI.lat, lon: FAUSTINI.lon, isPrimary: false, isFeatured: true,
  },
  {
    id: CABEUS.id, dropdownLabel: `${spIdLabel(CABEUS.id)} Cabeus`, shortLabel: CABEUS.label,
    lat: CABEUS.lat, lon: CABEUS.lon, isPrimary: false, isFeatured: true,
  },
  ...CANDIDATES.map((c): SiteDirectoryEntry => ({
    id: c.id, dropdownLabel: c.isPrimary ? `${c.label} (Primary)` : c.label, shortLabel: c.label,
    lat: c.lat, lon: c.lon, isPrimary: c.isPrimary, isFeatured: false,
  })),
];

// ── Mission narrative steps ─────────────────────────────────────
export const MISSION_STEPS = [
  { id: "discover",  label: "01 — Discover",  headline: "336 PSRs Screened",     sub: "Chandrayaan-2 DFSAR L-band radar, south pole catalog" },
  { id: "analyze",   label: "02 — Analyze",   headline: "4 Radar Metrics",        sub: "Pv · CPR · SERD · T-Ratio versus surroundings baseline" },
  { id: "map",       label: "03 — Map",       headline: "20 m/px LOLA DEM",       sub: "Real NASA GSFC elevation, slope and roughness" },
  { id: "detect",    label: "04 — Detect",    headline: "YOLOv8 Boulder AI",      sub: "ShadowCam imagery, Zero-DCE enhancement, object detection" },
  { id: "traverse",  label: "05 — Traverse",  headline: "Multi-objective Path",   sub: "Hazard-weighted rover traverse to crater interior" },
] as const;

export type CandidateId = typeof CANDIDATES[number]["id"];
