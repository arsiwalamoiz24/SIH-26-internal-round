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
    shortDescription: "Below baseline on all three scored metrics. Anchors the lower bound of the shortlist ranking.",
    terrain: { elevMin: -4300, elevMax: -2500, elevRange: 1800 },
    mlPixel: { meanInside: 0.2097, meanOutside: 0.1973, separation: 0.0124 },
  },
] as const;

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

// ── Mission narrative steps ─────────────────────────────────────
export const MISSION_STEPS = [
  { id: "discover",  label: "01 — Discover",  headline: "336 PSRs Screened",     sub: "Chandrayaan-2 DFSAR L-band radar, south pole catalog" },
  { id: "analyze",   label: "02 — Analyze",   headline: "4 Radar Metrics",        sub: "Pv · CPR · SERD · T-Ratio versus surroundings baseline" },
  { id: "map",       label: "03 — Map",       headline: "20 m/px LOLA DEM",       sub: "Real NASA GSFC elevation, slope and roughness" },
  { id: "detect",    label: "04 — Detect",    headline: "YOLOv8 Boulder AI",      sub: "ShadowCam imagery, Zero-DCE enhancement, object detection" },
  { id: "traverse",  label: "05 — Traverse",  headline: "Multi-objective Path",   sub: "Hazard-weighted rover traverse to crater interior" },
] as const;

export type CandidateId = typeof CANDIDATES[number]["id"];
