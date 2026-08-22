import { NextResponse } from "next/server";
import scienceData from "@/data/prism_science_data.json";

export async function GET() {
  return NextResponse.json({
    provenance: {
      source_type: "DERIVED",
      model_name: "Multi-Sensor Radar Agreement & Anomaly SNR Budget",
      assumptions: scienceData.primaryTarget.confidenceBudget.assumptions,
    },
    confidenceBudget: scienceData.primaryTarget.confidenceBudget,
    baselineStats: scienceData.baselineStats,
  });
}
