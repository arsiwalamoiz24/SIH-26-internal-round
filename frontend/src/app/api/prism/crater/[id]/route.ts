import { NextRequest, NextResponse } from "next/server";
import scienceData from "@/data/prism_science_data.json";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const detailedCraters = scienceData.detailedCraters as Record<string, any>;
  
  const crater = detailedCraters[id] || scienceData.primaryTarget.craterStats;

  return NextResponse.json({
    provenance: {
      source_type: "REAL",
      instrument: "Chandrayaan-2 DFSAR L-Band (2.5m/px)",
      psrBoundarySource: "LOLA Polar PSR Polygon",
      model_status: "Probabilistic Likelihood & Volume Estimate derived from radar evidence",
    },
    crater,
    confidenceBudget: scienceData.primaryTarget.confidenceBudget,
    volumeModel: scienceData.primaryTarget.volumeModel,
    evidenceGrid: scienceData.primaryTarget.evidenceGrid,
  });
}
