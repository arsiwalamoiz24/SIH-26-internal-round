import { NextResponse } from "next/server";
import scienceData from "@/data/prism_science_data.json";

export async function GET() {
  return NextResponse.json({
    provenance: {
      source_type: "DERIVED",
      landing_model: "Geometric Buffer & Radar Roughness Safety Scorer",
      trajectory_model: "Multi-Objective Pareto Graph Optimization (Safety, Discovery, Balanced)",
      slope_reference: "LOLA South-Polar Reference Baseline (live DEM pending)",
    },
    targetCrater: scienceData.primaryTarget.craterStats,
    landingSites: scienceData.primaryTarget.landingSites,
    drillSites: scienceData.primaryTarget.drillSites,
    roverPaths: scienceData.primaryTarget.roverPaths,
  });
}
