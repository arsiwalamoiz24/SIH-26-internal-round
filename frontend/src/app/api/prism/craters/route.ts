import { NextResponse } from "next/server";
import scienceData from "@/data/prism_science_data.json";

export async function GET() {
  return NextResponse.json({
    provenance: {
      source_type: "REAL",
      dataset: "Chandrayaan-2 DFSAR L-Band & NASA LOLA PSR Catalog",
      timestamp: new Date().toISOString(),
      version: scienceData.metadata.version,
    },
    metadata: scienceData.metadata,
    baselineStats: scienceData.baselineStats,
    psrCatalog: scienceData.psrCatalog,
    detailedCraters: scienceData.detailedCraters,
  });
}
