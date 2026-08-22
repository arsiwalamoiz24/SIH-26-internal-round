// Mission Overview — Data Contract (Phase 1, notebook-derived)
//
// Every number in this file is copied from the printed/plotted outputs of the
// team's Colab analysis notebook (Chandrayaan-2 DFSAR South Pole screening),
// NOT invented for the UI. Where a stat could not be derived from the notebook
// (slope, illumination, rover paths, a literal ice volume in m³, a calibrated
// confidence score), it is intentionally left out rather than faked — see the
// `connected` flags below and PRISM_DATA_STATUS.md for the full breakdown.
//
// Source products:
//  - L4 Y4R mosaic (evn/vol/odd/hlx) — ch2_sar_ndxl_20250630my4rspwest_d_fp_xxx
//  - L3C CPR mosaic (cpr/srd/trt)    — ch2_sar_ndxl_20250630mpcpspwest_d_fp_xxx
//  - LOLA South Pole PSR catalog     — NAC_POLE_PSR_SOUTH (LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL)
// Grid: Moon 2000 South Polar Stereographic, ~25 m/px (24181 x 24794 native; analyzed at a 1500px overview + full-res crops per candidate).

export interface CandidateSite {
  psrId: string;
  lat: number;
  lon: number;
  areaKm2: number;
  pvMean: number;
  pvDiffVsSurroundings: number;
  cprDiffVsSurroundings: number;
  cprPctPixelsAboveOne: number;
  trtDiffVsSurroundings: number;
  agreeingSignals: number; // of 3 (Pv, CPR, T-Ratio) elevated vs local surroundings
}

export interface MissionOverviewData {
  connected: {
    psrCatalog: true;
    pvScreening: true;
    cprCrossCheck: true;
    landingSafety: false;
    roverTraverse: false;
    liveBackend: false;
  };
  dataset: {
    gridResolutionM: number;
    psrCatalogTotal: number;
    psrWithRadarCoverage: number;
    psrCoveragePct: number;
  };
  pvFraction: {
    mean: number;
    median: number;
    p90: number;
  };
  psrAreaFractionOfOverview: number;
  tierCounts: {
    outsidePsr: number;
    psrLowPv: number;
    psrModeratePv: number;
    psrHighPv: number;
  };
  globalCprAboveOnePct: number;
  topCandidate: CandidateSite;
  shortlist: CandidateSite[];
}

export function getMissionOverview(): MissionOverviewData {
  const shortlist: CandidateSite[] = [
    { psrId: "SP_840980_0797630", lat: -84.098, lon: 79.764, areaKm2: 14.2, pvMean: 0.507, pvDiffVsSurroundings: 0.081, cprDiffVsSurroundings: 0.099, cprPctPixelsAboveOne: 7.33, trtDiffVsSurroundings: 0.121, agreeingSignals: 3 },
    { psrId: "SP_832640_0090770", lat: -83.264, lon: 9.077, areaKm2: 32.5, pvMean: 0.518, pvDiffVsSurroundings: 0.024, cprDiffVsSurroundings: 0.056, cprPctPixelsAboveOne: 10.79, trtDiffVsSurroundings: 0.043, agreeingSignals: 3 },
    { psrId: "SP_809570_2454450", lat: -80.957, lon: 245.445, areaKm2: 9.2, pvMean: 0.427, pvDiffVsSurroundings: 0.049, cprDiffVsSurroundings: -0.010, cprPctPixelsAboveOne: 0.10, trtDiffVsSurroundings: 0.043, agreeingSignals: 2 },
    { psrId: "SP_819860_1568660", lat: -81.986, lon: 156.866, areaKm2: 10.7, pvMean: 0.500, pvDiffVsSurroundings: 0.006, cprDiffVsSurroundings: 0.025, cprPctPixelsAboveOne: 10.41, trtDiffVsSurroundings: 0.014, agreeingSignals: 3 },
    { psrId: "SP_842420_0421060", lat: -84.242, lon: 42.106, areaKm2: 25.5, pvMean: 0.526, pvDiffVsSurroundings: 0.016, cprDiffVsSurroundings: -0.016, cprPctPixelsAboveOne: 0.14, trtDiffVsSurroundings: -0.037, agreeingSignals: 1 },
    { psrId: "SP_817950_1586580", lat: -81.795, lon: 158.658, areaKm2: 43.4, pvMean: 0.487, pvDiffVsSurroundings: -0.021, cprDiffVsSurroundings: -0.080, cprPctPixelsAboveOne: 0.00, trtDiffVsSurroundings: -0.090, agreeingSignals: 0 },
    { psrId: "SP_830080_0535120", lat: -83.008, lon: 53.512, areaKm2: 22.5, pvMean: 0.490, pvDiffVsSurroundings: -0.068, cprDiffVsSurroundings: -0.155, cprPctPixelsAboveOne: 7.22, trtDiffVsSurroundings: -0.167, agreeingSignals: 0 },
  ];

  return {
    connected: {
      psrCatalog: true,
      pvScreening: true,
      cprCrossCheck: true,
      landingSafety: false,
      roverTraverse: false,
      liveBackend: false,
    },
    dataset: {
      gridResolutionM: 25,
      psrCatalogTotal: 653,
      psrWithRadarCoverage: 336,
      psrCoveragePct: 51.5,
    },
    pvFraction: {
      mean: 0.262,
      median: 0.252,
      p90: 0.416,
    },
    psrAreaFractionOfOverview: 4.48,
    tierCounts: {
      outsidePsr: 2129453,
      psrLowPv: 34611,
      psrModeratePv: 20907,
      psrHighPv: 8029,
    },
    globalCprAboveOnePct: 0.051,
    topCandidate: shortlist[0],
    shortlist,
  };
}
