/**
 * PRISM demo data layer.
 *
 * This file draws a hard line between two kinds of data:
 *
 * - REAL_* constants: transcribed verbatim from the science pipeline's real output files
 *   in `PRISM/outputs/**`. Every value here traces back to a cited source file. Nothing in
 *   this block is computed, estimated, or invented by the frontend.
 *
 * - SYNTHETIC_* constants: fabricated for demo/UI purposes only (map interaction, comparison
 *   charts, time series), because the pipeline does not yet have full per-metric results for
 *   every PSR, or historical multi-temporal measurements. These must never be presented as
 *   real observations.
 *
 * Every object in both groups carries an explicit `source` field
 * ("real_pipeline" | "synthetic_demo") so the two can never be silently mixed.
 */

export type DataSource = "real_pipeline" | "synthetic_demo";

export type CandidateStatus =
  | "potential_ice_candidate"
  | "under_review"
  | "low_priority";

export interface RadarMetric {
  mean: number;
  median: number;
  percentile: number;
  source: DataSource;
}

export interface DopFormulations {
  linearHhVvMean: number;
  linearHhVvMedian: number;
  hybridLhLvMean: number;
  hybridLhLvMedian: number;
  eigenvaluePurityMean: number;
  validPixels: number;
  pctNan: number;
  source: DataSource;
}

export interface TerrainStats {
  meanSlopeDeg: number;
  pctExceedsHazardThreshold: number;
  hazardThresholdDeg: number;
  triMeters: number;
  source: DataSource;
}

export interface MlAnomalyResult {
  method: string;
  nSamples: number;
  candidateRank: number;
  anomalyScore: number;
  isAnomaly: boolean;
  source: DataSource;
}

export interface EvidenceScore {
  score: number;
  rank: number;
  outOf: number;
  source: DataSource;
}

export interface AcquisitionInfo {
  acquisitionId: string;
  productId: string;
  station: string;
  date: string;
  gridCsvPath: string;
  dopWindow: {
    startLine: number;
    endLine: number;
    nLines: number;
    rangeSamples: number;
    validPixels: number;
    pctNan: number;
  };
  source: DataSource;
}

export interface RealCandidate {
  id: string;
  latitude: number;
  longitude: number;
  status: CandidateStatus;
  statusLabel: string;
  subtext: string;
  pv: RadarMetric;
  cpr: RadarMetric;
  serd: RadarMetric;
  tRatio: RadarMetric;
  dop: DopFormulations;
  terrain: TerrainStats;
  ml: MlAnomalyResult;
  evidenceScore: EvidenceScore;
  acquisition: AcquisitionInfo;
  coverageNote: string;
  images: {
    overview: string;
    radarMetrics: string;
    radarComposite: string;
    dop: string;
    dopHistogram: string;
    terrain: string;
    terrainComposite: string;
    evidenceMap: string;
  };
  finalInterpretation: string;
  source: DataSource;
}

/**
 * REAL DATA — transcribed from PRISM/outputs/objective1/PHYSICS_RESULTS.json,
 * PRISM/outputs/objective2/SP_840980_0797630_terrain_stats.json,
 * PRISM/outputs/objective1/dop/candidate_dop.json,
 * PRISM/outputs/objective1/ml/isolation_forest_results.json,
 * PRISM/outputs/objective1/evidence_score/physics_evidence_score.json.
 * Verified against the source files field-by-field; no recomputation performed here.
 */
export const REAL_CANDIDATE: RealCandidate = {
  id: "SP_840980_0797630",
  latitude: -84.098,
  longitude: 79.764,
  status: "potential_ice_candidate",
  statusLabel: "Potential Ice Candidate",
  subtext:
    "Physics and radar indicators are consistent with an anomalous PSR. Independent ice confirmation is not available.",
  pv: {
    mean: 0.4543111324310303,
    median: 0.46922242641448975,
    percentile: 93.90888766236904,
    source: "real_pipeline",
  },
  cpr: {
    mean: 0.5649844408035278,
    median: 0.5424538850784302,
    percentile: 97.20055281658718,
    source: "real_pipeline",
  },
  serd: {
    mean: 0.6729207038879395,
    median: 0.6690033674240112,
    percentile: 4.261376063745663,
    source: "real_pipeline",
  },
  tRatio: {
    mean: 0.5707418918609619,
    median: 0.5297855138778687,
    percentile: 95.80992400029359,
    source: "real_pipeline",
  },
  dop: {
    linearHhVvMean: 0.6804845929145813,
    linearHhVvMedian: 0.7082269191741943,
    hybridLhLvMean: 0.5935717847805299,
    hybridLhLvMedian: 0.6065349504207269,
    eigenvaluePurityMean: 0.908509373664856,
    validPixels: 488000,
    pctNan: 0.0,
    source: "real_pipeline",
  },
  terrain: {
    meanSlopeDeg: 22.075857162475586,
    pctExceedsHazardThreshold: 78.63204631034677,
    hazardThresholdDeg: 20,
    triMeters: 6.293287354510409,
    source: "real_pipeline",
  },
  ml: {
    method: "Unsupervised Isolation Forest",
    nSamples: 336,
    candidateRank: 40,
    anomalyScore: 0.005606031542763956,
    isAnomaly: true,
    source: "real_pipeline",
  },
  evidenceScore: {
    score: 1.0,
    rank: 1,
    outOf: 7,
    source: "real_pipeline",
  },
  acquisition: {
    acquisitionId: "ch2_sar_ncxl_20220318t135736694_d_fp_d18",
    productId: "2238611",
    station: "d18",
    date: "2022-03-18",
    gridCsvPath:
      "geometry/calibrated/20220318/ch2_sar_ncxl_20220318t135736694_g_sli_xx_fp_xx_d18.csv",
    dopWindow: {
      startLine: 218616,
      endLine: 220616,
      nLines: 2000,
      rangeSamples: 244,
      validPixels: 488000,
      pctNan: 0.0,
    },
    source: "real_pipeline",
  },
  coverageNote:
    "Confirmed by image-footprint polygon and per-pixel Grid CSV.",
  images: {
    overview: "/prism/candidate_overview.png",
    radarMetrics: "/prism/candidate_radar_metrics.png",
    radarComposite: "/prism/SP_840980_0797630_radar_composite.png",
    dop: "/prism/candidate_dop.png",
    dopHistogram: "/prism/candidate_dop_histogram.png",
    terrain: "/prism/candidate_terrain.png",
    terrainComposite: "/prism/SP_840980_0797630_terrain_composite.png",
    evidenceMap: "/prism/candidate_evidence_map.png",
  },
  finalInterpretation:
    "PRISM identifies this location as a high-priority potential ice candidate based on the combined radar, polarimetric, terrain and anomaly evidence. This result is not an independent confirmation of water ice.",
  source: "real_pipeline",
};

export const DOP_THRESHOLD_WARNING =
  "Not validated against published ground truth. Running this same pipeline on Sinha et al. 2026's own confirmed-ice craters returns DOP ~6x their reported 0.10-0.13, and 8 hypotheses (window size, small-sample bias, absolute and relative calibration, Zhao 2024 multilook, self-derived and full Ainsworth 2006 crosstalk, and an independent acquisition) failed to close the gap. This is an OPEN PROBLEM, not a metric to set aside: the paper's own Supplementary Fig. 6 shows rough terrain reaching CPR 1.1 at DOP 0.17, and states that high CPR alone is insufficient -- the combined CPR-DOP criterion is what separates surface roughness from subsurface volumetric scattering. PRISM's CPR reproduces the paper and is real evidence the radar processing is sound, but on its own it cannot tell ice from rough rock. See PRISM/docs/SINHA_SUPPLEMENTARY_FINDINGS.md.";

export const TERRAIN_THRESHOLD_LABEL = "Unvalidated project threshold";

export const EVIDENCE_SCORE_TOOLTIP =
  "Transparent ranking score derived from project physics indicators. It is not a probability of water ice.";

export const ML_INTERPRETATION =
  "Candidate exhibits an anomalous physics profile relative to the evaluated PSR population.";

// ---------------------------------------------------------------------------
// SYNTHETIC DEMO DATA — fabricated for interactive UI only. Never measured.
// ---------------------------------------------------------------------------

export interface SyntheticCandidate {
  id: string;
  latitude: number;
  longitude: number;
  pv: number;
  cpr: number;
  serd: number;
  t_ratio: number;
  dop: number;
  terrain_slope: number;
  tri: number;
  anomaly_score: number;
  status: CandidateStatus;
  source: "synthetic_demo";
}

/**
 * ~25 fabricated PSR candidates scattered around the real candidate's coordinates, purely to
 * demonstrate map interaction, filtering, and comparison charts. None of these are satellite
 * observations. Values are plausible but invented.
 */
function makeSyntheticCandidates(): SyntheticCandidate[] {
  const seedOffsets: Array<[number, number]> = [
    [-1.8, 3.1], [1.2, -2.4], [-2.6, -1.1], [0.6, 2.9], [2.1, 1.4],
    [-0.9, -3.2], [3.0, 0.3], [-1.4, 1.9], [1.9, -0.7], [-3.1, 0.9],
    [0.3, -1.6], [-2.2, 2.4], [2.6, -1.9], [-0.5, 3.4], [1.5, 1.1],
    [-1.1, -0.4], [2.9, 2.2], [-2.9, -2.1], [0.9, 0.6], [-0.2, -2.8],
    [1.7, -3.0], [-1.6, 0.2], [3.2, -0.9], [-0.7, 1.6], [2.3, 3.1],
  ];

  const statuses: CandidateStatus[] = [
    "potential_ice_candidate",
    "under_review",
    "low_priority",
  ];

  return seedOffsets.map(([dLat, dLon], i) => {
    // Deterministic pseudo-random spread so the demo is stable across reloads.
    const r = (n: number) => Math.abs(Math.sin(i * 12.9898 + n * 78.233) * 43758.5453) % 1;
    const pv = 0.15 + r(1) * 0.55;
    const cpr = 0.15 + r(2) * 0.55;
    const serd = 0.3 + r(3) * 0.6;
    const t_ratio = 0.2 + r(4) * 0.55;
    const dop = 0.3 + r(5) * 0.5;
    const terrain_slope = 6 + r(6) * 20;
    const tri = 1.5 + r(7) * 6;
    const anomaly_score = r(8) * 0.02;
    const status = statuses[Math.floor(r(9) * statuses.length)];

    return {
      id: `SP_${840000 + i * 733}_${97000 + i * 1291}`,
      latitude: REAL_CANDIDATE.latitude + dLat,
      longitude: REAL_CANDIDATE.longitude + dLon,
      pv: Number(pv.toFixed(3)),
      cpr: Number(cpr.toFixed(3)),
      serd: Number(serd.toFixed(3)),
      t_ratio: Number(t_ratio.toFixed(3)),
      dop: Number(dop.toFixed(3)),
      terrain_slope: Number(terrain_slope.toFixed(1)),
      tri: Number(tri.toFixed(1)),
      anomaly_score: Number(anomaly_score.toFixed(4)),
      status,
      source: "synthetic_demo" as const,
    };
  });
}

export const SYNTHETIC_CANDIDATES: SyntheticCandidate[] = makeSyntheticCandidates();

/** Shape shared by map markers regardless of whether they're real or synthetic. */
export type CandidateMarker = Omit<SyntheticCandidate, "source"> & { source: DataSource };

/** The real candidate, reshaped into the same map-marker shape as the synthetic set, for map display. */
export const REAL_CANDIDATE_MARKER: CandidateMarker = {
  id: REAL_CANDIDATE.id,
  latitude: REAL_CANDIDATE.latitude,
  longitude: REAL_CANDIDATE.longitude,
  pv: REAL_CANDIDATE.pv.mean,
  cpr: REAL_CANDIDATE.cpr.mean,
  serd: REAL_CANDIDATE.serd.mean,
  t_ratio: REAL_CANDIDATE.tRatio.mean,
  dop: REAL_CANDIDATE.dop.linearHhVvMean,
  terrain_slope: REAL_CANDIDATE.terrain.meanSlopeDeg,
  tri: REAL_CANDIDATE.terrain.triMeters,
  anomaly_score: REAL_CANDIDATE.ml.anomalyScore,
  status: "potential_ice_candidate",
  source: "real_pipeline",
};

export interface SyntheticTimeSeriesPoint {
  date: string;
  pv: number;
  cpr: number;
  serd: number;
  t_ratio: number;
  source: "synthetic_demo";
}

/**
 * SYNTHETIC DEMONSTRATION DATA — NOT MEASURED OBSERVATIONS.
 * Smooth plausible variation around the real candidate's mean values, for chart interaction only.
 * The pipeline has a single real acquisition for this candidate, not a multi-temporal record.
 */
function makeSyntheticTimeSeries(): SyntheticTimeSeriesPoint[] {
  const months = [
    "2021-09", "2021-11", "2022-01", "2022-03", "2022-05",
    "2022-07", "2022-09", "2022-11", "2023-01", "2023-03",
  ];
  const base = {
    pv: REAL_CANDIDATE.pv.mean,
    cpr: REAL_CANDIDATE.cpr.mean,
    serd: REAL_CANDIDATE.serd.mean,
    t_ratio: REAL_CANDIDATE.tRatio.mean,
  };
  return months.map((date, i) => {
    const wobble = Math.sin(i * 0.8) * 0.03 + Math.cos(i * 0.35) * 0.015;
    return {
      date,
      pv: Number((base.pv + wobble).toFixed(3)),
      cpr: Number((base.cpr + wobble * 0.8).toFixed(3)),
      serd: Number((base.serd - wobble * 0.6).toFixed(3)),
      t_ratio: Number((base.t_ratio + wobble * 1.1).toFixed(3)),
      source: "synthetic_demo" as const,
    };
  });
}

export const SYNTHETIC_TIMESERIES: SyntheticTimeSeriesPoint[] = makeSyntheticTimeSeries();

export const SYNTHETIC_TIMESERIES_LABEL =
  "SYNTHETIC DEMONSTRATION DATA — NOT MEASURED OBSERVATIONS";

export function findCandidateById(
  id: string
): { kind: "real"; candidate: RealCandidate } | { kind: "synthetic"; candidate: SyntheticCandidate } | null {
  if (id === REAL_CANDIDATE.id) {
    return { kind: "real", candidate: REAL_CANDIDATE };
  }
  const synthetic = SYNTHETIC_CANDIDATES.find((c) => c.id === id);
  if (synthetic) {
    return { kind: "synthetic", candidate: synthetic };
  }
  return null;
}
