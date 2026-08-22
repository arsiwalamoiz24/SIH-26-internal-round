// Data Contract & Access Layer for PRISM UI
// Connects the frontend to real Chandrayaan-2 DFSAR findings and transparent derived models.

import scienceData from "@/data/prism_science_data.json";

export interface ProvenanceMetadata {
  source_type: "REAL" | "DERIVED" | "SIMULATED";
  dataset?: string;
  instrument?: string;
  model_name?: string;
  assumptions?: string | Record<string, any>;
  uncertainty?: string;
  version?: string;
}

export interface ConfidenceBudget {
  overall: number;
  factors: {
    radarAgreement: "Low" | "Moderate" | "High";
    dataQuality: "Suboptimal" | "Optimal";
    modelCertainty: number;
    anomalySignificanceZ?: number;
    pvAnomalyDelta?: number;
    cprAnomalyDelta?: number;
  };
  provenance: ProvenanceMetadata;
}

export interface VolumeEstimate {
  mean: number;
  uncertainty: number;
  unit: string;
  assumptions: {
    craterAreaKm2: number;
    highPvFraction: number;
    radarPenetrationDepthMeters: number;
    assumedIceVolumeFractionPct: number;
    iceFractionNature: string;
  };
  provenance: ProvenanceMetadata;
}

export interface DrillSite {
  id: string;
  name: string;
  confidence: number;
  coordinates: { lat: number; lon: number };
  rationale: string;
  provenance: ProvenanceMetadata;
}

export interface LandingSite {
  id: string;
  name: string;
  coordinates?: { lat: number; lon: number };
  distToIce: number;
  sunlight: number;
  safetyScore: number;
  scienceValue: number;
  slope: number;
  rank: number;
  rationale: string;
  scoringBreakdown: {
    slopeSafetyScore: number;
    iceProximityScore: number;
    powerSunlightScore: number;
  };
  provenance: ProvenanceMetadata;
}

export interface RoverWaypoint {
  id: string;
  title: string;
  note: string;
  distKm: number;
  localPv: number;
}

export interface RoverPath {
  id: string;
  type: "safety" | "discovery" | "balanced";
  name: string;
  color: string;
  lengthKm: number;
  traverseCost: number;
  points: [number, number, number][]; // x, y, z for ThreeJS
  waypoints: RoverWaypoint[];
  provenance: ProvenanceMetadata;
}

export interface TargetCraterStats {
  psrId: string;
  name: string;
  latitude: number;
  longitude: number;
  areaKm2: number;
  pvMeanInside: number;
  pvMedianInside: number;
  pvMeanSurroundings: number;
  pvAnomaly: number;
  cprMeanInside: number;
  cprMeanSurroundings: number;
  cprAnomaly: number;
  cprGt1FractionPct: number;
  serdMeanInside: number;
  serdMeanSurroundings: number;
  serdDifference: number;
  highPvFraction: number;
  moderatePlusFraction: number;
  provenance: ProvenanceMetadata;
}

export interface EvidenceGridData {
  dimensions: [number, number];
  description: string;
  pvGrid: number[][];
  cprGrid: number[][];
  probIceGrid: number[][];
  psrMaskGrid: boolean[][];
}

// -------------------------------------------------------------------------
// Accessor Methods (Synchronous + Reactive)
// -------------------------------------------------------------------------

export function getTargetCrater(): TargetCraterStats {
  const c = scienceData.primaryTarget.craterStats;
  return {
    ...c,
    provenance: {
      source_type: "REAL",
      instrument: "Chandrayaan-2 DFSAR L-Band (2.5m/px)",
      dataset: "L4 Mosaic (ch2_sar_ndxl_20250630my4rspwest)",
    },
  };
}

export function getConfidenceBudget(): ConfidenceBudget {
  const cb = scienceData.primaryTarget.confidenceBudget;
  return {
    overall: cb.overallScore,
    factors: {
      radarAgreement: cb.factors.radarAgreement as "High" | "Moderate" | "Low",
      dataQuality: cb.factors.dataQuality as "Optimal" | "Suboptimal",
      modelCertainty: cb.factors.modelCertaintyPct,
      anomalySignificanceZ: cb.factors.anomalySignificanceZ,
      pvAnomalyDelta: cb.factors.pvAnomalyDelta,
      cprAnomalyDelta: cb.factors.cprAnomalyDelta,
    },
    provenance: {
      source_type: "DERIVED",
      model_name: cb.model_name,
      assumptions: cb.assumptions,
    },
  };
}

export function getVolumeEstimate(userAssumedIceFractionPct: number = 10.0): VolumeEstimate {
  const vm = scienceData.primaryTarget.volumeModel;
  const areaM2 = vm.assumptions.craterAreaKm2 * 1e6;
  const penDepthM = vm.assumptions.radarPenetrationDepthMeters;
  const highPvFrac = vm.assumptions.highPvFraction;
  
  const calculatedMean = areaM2 * highPvFrac * penDepthM * (userAssumedIceFractionPct / 100.0);
  const calculatedUncertainty = calculatedMean * 0.185;

  return {
    mean: Math.round(calculatedMean),
    uncertainty: Math.round(calculatedUncertainty),
    unit: "m³",
    assumptions: {
      craterAreaKm2: vm.assumptions.craterAreaKm2,
      highPvFraction: vm.assumptions.highPvFraction,
      radarPenetrationDepthMeters: penDepthM,
      assumedIceVolumeFractionPct: userAssumedIceFractionPct,
      iceFractionNature: "Assumed model parameter (not directly measured)",
    },
    provenance: {
      source_type: "DERIVED",
      model_name: "Indicative Volumetric Skin-Depth Model",
      assumptions: vm.assumptions,
    },
  };
}

export function getDrillSites(): DrillSite[] {
  return (scienceData.primaryTarget.drillSites as any[]).map((ds) => ({
    id: ds.id,
    name: ds.name,
    confidence: ds.confidence,
    coordinates: ds.coordinates,
    rationale: ds.rationale,
    provenance: {
      source_type: ds.provenance.source_type as "REAL" | "DERIVED" | "SIMULATED",
      method: ds.provenance.method,
    },
  }));
}

export function getLandingSites(): LandingSite[] {
  return (scienceData.primaryTarget.landingSites as any[]).map((ls) => ({
    id: ls.id,
    name: ls.name,
    coordinates: ls.coordinates,
    distToIce: ls.distToIceKm,
    sunlight: ls.sunlightHours,
    safetyScore: ls.safetyScore,
    scienceValue: ls.scienceValue,
    slope: ls.slopeDeg,
    rank: ls.rank,
    rationale: ls.rationale,
    scoringBreakdown: ls.scoringBreakdown,
    provenance: {
      source_type: ls.provenance.source_type as "REAL" | "DERIVED" | "SIMULATED",
      assumptions: ls.provenance,
    },
  }));
}

export function getRoverPaths(): RoverPath[] {
  return (scienceData.primaryTarget.roverPaths as any[]).map((rp) => ({
    id: rp.id,
    type: rp.type,
    name: rp.name,
    color: rp.color,
    lengthKm: rp.lengthKm,
    traverseCost: rp.traverseCost,
    points: rp.points3D,
    waypoints: rp.waypoints,
    provenance: {
      source_type: rp.provenance.source_type as "REAL" | "DERIVED" | "SIMULATED",
      model_name: rp.provenance.solver,
    },
  }));
}

export function getEvidenceGrid(): EvidenceGridData {
  const eg = scienceData.primaryTarget.evidenceGrid;
  return {
    dimensions: eg.dimensions as [number, number],
    description: eg.description,
    pvGrid: eg.pvGrid,
    cprGrid: eg.cprGrid,
    probIceGrid: eg.probIceGrid,
    psrMaskGrid: eg.psrMaskGrid,
  };
}

export function getBaselineStats() {
  return scienceData.baselineStats;
}

export interface PhysicsEvidenceScore {
  score: number;
  rank: number;
  rankOf: number;
  deltaPv: number;
  deltaCpr: number;
  deltaTRatio: number;
  deltaSerdExcluded: number;
  serdExclusionReason: string;
  weighting: string;
  notWhat: string;
  provenance: ProvenanceMetadata;
}

export function getPhysicsEvidenceScore(): PhysicsEvidenceScore {
  const pes = scienceData.primaryTarget.physicsEvidenceScore;
  return {
    score: pes.score,
    rank: pes.rank,
    rankOf: pes.rankOf,
    deltaPv: pes.deltaPv,
    deltaCpr: pes.deltaCpr,
    deltaTRatio: pes.deltaTRatio,
    deltaSerdExcluded: pes.deltaSerdExcluded,
    serdExclusionReason: pes.serdExclusionReason,
    weighting: pes.weighting,
    notWhat: pes.notWhat,
    provenance: {
      source_type: "REAL",
      dataset: pes.source,
    },
  };
}

export interface MlAnomalyScore {
  model: string;
  nSamples: number;
  features: string[];
  anomalyScore: number;
  anomalyRank: number;
  anomalyRankOf: number;
  isAnomalyLabel: boolean;
  circularityWarning: string;
  provenance: ProvenanceMetadata;
}

export function getMlAnomalyScore(): MlAnomalyScore {
  const ml = scienceData.primaryTarget.mlAnomalyScore;
  return {
    model: ml.model,
    nSamples: ml.nSamples,
    features: ml.features,
    anomalyScore: ml.anomalyScore,
    anomalyRank: ml.anomalyRank,
    anomalyRankOf: ml.anomalyRankOf,
    isAnomalyLabel: ml.isAnomalyLabel,
    circularityWarning: ml.circularityWarning,
    provenance: {
      source_type: "REAL",
      dataset: ml.source,
    },
  };
}

export interface DopSummary {
  linearPolDopMean: number;
  linearPolDopMedian: number;
  hybridPolDopMean: number;
  eigenvaluePurityWholeWindow: number;
  nValidPx: number;
  acquisition: string;
  bestSupportedFormulation: string;
  calibrationApplied: string;
  note: string;
  provenance: ProvenanceMetadata;
}

export function getDopSummary(): DopSummary {
  const dop = scienceData.primaryTarget.dop.candidateSpecific;
  return {
    linearPolDopMean: dop.linearPolDopMean,
    linearPolDopMedian: dop.linearPolDopMedian,
    hybridPolDopMean: dop.hybridPolDopMean,
    eigenvaluePurityWholeWindow: dop.eigenvaluePurityWholeWindow,
    nValidPx: dop.nValidPx,
    acquisition: dop.acquisition,
    bestSupportedFormulation: dop.bestSupportedFormulation,
    calibrationApplied: dop.calibrationApplied,
    note: dop.note,
    provenance: {
      source_type: "REAL",
      dataset: dop.source,
    },
  };
}

export interface TerrainStats {
  windowSizeKm: number;
  slope: {
    meanDegWholeWindow: number;
    medianDegWholeWindow: number;
    maxDegWholeWindow: number;
    pctSafeLt10deg: number;
    pctCaution10to20deg: number;
    pctHazardGte20deg: number;
    meanDegPsrInterior: number;
    pctHazardGte20degPsrInterior: number;
    meanDegApproachTerrain: number;
    pctHazardGte20degApproachTerrain: number;
    thresholdCaveat: string;
  };
  elevation: {
    meanM: number;
    minM: number;
    maxM: number;
    rangeM: number;
  };
  roughnessTri: {
    meanTriM: number;
    medianTriM: number;
    meanTriMPsrInterior: number;
    meanTriMApproachTerrain: number;
  };
  interpretation: string;
  provenance: ProvenanceMetadata;
}

export interface PixelAnomalyScore {
  model: string;
  features: string[];
  featuresIndependent: boolean;
  nPixelsValid: number;
  windowShapePx: [number, number];
  meanIceLikelihoodInsidePsr: number;
  meanIceLikelihoodOutsidePsr: number;
  definition: string;
  note: string;
  provenance: ProvenanceMetadata;
}

export function getPixelAnomalyScore(): PixelAnomalyScore {
  const p = scienceData.primaryTarget.pixelAnomalyScore;
  return {
    model: p.model,
    features: p.features,
    featuresIndependent: p.featuresIndependent,
    nPixelsValid: p.nPixelsValid,
    windowShapePx: p.windowShapePx as [number, number],
    meanIceLikelihoodInsidePsr: p.meanIceLikelihoodInsidePsr,
    meanIceLikelihoodOutsidePsr: p.meanIceLikelihoodOutsidePsr,
    definition: p.definition,
    note: p.note,
    provenance: {
      source_type: "REAL",
      dataset: p.source,
    },
  };
}

export function getTerrainStats(): TerrainStats {
  const t = scienceData.primaryTarget.terrain;
  return {
    windowSizeKm: t.windowSizeKm,
    slope: t.slope,
    elevation: t.elevation,
    roughnessTri: t.roughnessTri,
    interpretation: t.interpretation,
    provenance: {
      source_type: "REAL",
      dataset: t.source,
    },
  };
}
