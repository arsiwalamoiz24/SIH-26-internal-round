"use client";

import Link from "next/link";
import { findCandidateById, REAL_CANDIDATE } from "@/data/prismDemoData";
import { DemoDataBadge } from "./DemoDataBadge";
import { EvidenceScoreBadge } from "./EvidenceScoreBadge";
import { PhysicsEvidenceCard } from "./PhysicsEvidenceCard";
import { DopPanel } from "./DopPanel";
import { TerrainPanel } from "./TerrainPanel";
import { MlPanel } from "./MlPanel";

export function CandidateDetailClient({ id }: { id: string }) {
  const result = findCandidateById(id);

  if (!result) {
    return (
      <main className="flex-1 overflow-y-auto bg-background flex items-center justify-center">
        <div className="text-center">
          <p className="font-h2 text-h2 text-on-surface mb-2">Candidate not found</p>
          <Link href="/" className="text-primary font-body-sm underline">
            Back to dashboard
          </Link>
        </div>
      </main>
    );
  }

  if (result.kind === "synthetic") {
    const s = result.candidate;
    return (
      <main className="flex-1 overflow-y-auto bg-background">
        <div className="px-grid-gutter pt-grid-gutter pb-8 flex flex-col gap-grid-gutter max-w-[900px] mx-auto">
          <Link href="/" className="font-body-sm text-primary text-[12px] hover:underline w-fit">
            ← Back to dashboard
          </Link>
          <div className="bg-surface-container-lowest tech-border rounded p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-h1 text-h1 text-on-surface">{s.id}</span>
              <DemoDataBadge source="synthetic_demo" />
            </div>
            <div className="bg-tertiary-container/10 border border-tertiary-container/40 rounded p-3 font-body-sm text-[12px] text-on-surface-variant mb-3">
              This is a synthetic demo candidate generated for map/comparison interaction only. It
              is not a real pipeline result. Only <strong>{REAL_CANDIDATE.id}</strong> has full
              real-pipeline validation — see its{" "}
              <Link href={`/candidate/${REAL_CANDIDATE.id}`} className="text-primary underline">
                candidate report
              </Link>
              .
            </div>
            <div className="font-data-md text-data-md text-on-surface-variant mono-nums mb-3">
              Lat {s.latitude.toFixed(3)}° &nbsp;Lon {s.longitude.toFixed(3)}°
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-data-sm text-[11px]">
              <Stat label="Pv" value={s.pv.toFixed(3)} />
              <Stat label="CPR" value={s.cpr.toFixed(3)} />
              <Stat label="SERD" value={s.serd.toFixed(3)} />
              <Stat label="T-Ratio" value={s.t_ratio.toFixed(3)} />
              <Stat label="DOP" value={s.dop.toFixed(3)} />
              <Stat label="Slope" value={`${s.terrain_slope.toFixed(1)}°`} />
              <Stat label="TRI" value={`${s.tri.toFixed(1)} m`} />
              <Stat label="Anomaly" value={s.anomaly_score.toFixed(4)} />
            </div>
          </div>
        </div>
      </main>
    );
  }

  const c = result.candidate;

  return (
    <main className="flex-1 overflow-y-auto bg-background">
      <div className="px-grid-gutter pt-grid-gutter pb-8 flex flex-col gap-grid-gutter max-w-[1100px] mx-auto">
        <Link href="/" className="font-body-sm text-primary text-[12px] hover:underline w-fit">
          ← Back to dashboard
        </Link>

        {/* HEADER */}
        <div className="bg-surface-container-lowest tech-border rounded p-4">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-h1 text-h1 text-on-surface">{c.id}</span>
            <DemoDataBadge source={c.source} />
          </div>
          <span className="bg-primary text-on-primary px-3 py-1 rounded font-body-sm font-semibold uppercase tracking-wider text-[12px] inline-block">
            {c.statusLabel}
          </span>
        </div>

        {/* LOCATION */}
        <Section title="Location">
          <div className="font-data-md text-data-md text-on-surface mono-nums">
            Lat {c.latitude.toFixed(3)}° &nbsp;Lon {c.longitude.toFixed(3)}°
          </div>
        </Section>

        {/* EVIDENCE SCORE */}
        <EvidenceScoreBadge evidence={c.evidenceScore} />

        {/* RADAR */}
        <Section title="Radar">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-grid-gutter">
            <PhysicsEvidenceCard label="Pv" metric={c.pv} interpretation="Elevated volume scattering." />
            <PhysicsEvidenceCard label="CPR" metric={c.cpr} interpretation="High circular polarization ratio." />
            <PhysicsEvidenceCard label="SERD" metric={c.serd} interpretation="Anomalously low vs. mosaic." flagged />
            <PhysicsEvidenceCard label="T-Ratio" metric={c.tRatio} interpretation="High transmit-ratio signal." />
          </div>
        </Section>

        {/* DOP */}
        <DopPanel dop={c.dop} dopImage={c.images.dop} histogramImage={c.images.dopHistogram} />

        {/* ACQUISITION */}
        <Section title="Acquisition">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-data-sm text-[11px]">
            <Stat label="Date" value={c.acquisition.date} />
            <Stat label="Product ID" value={c.acquisition.productId} />
            <Stat label="Station" value={c.acquisition.station} />
            <Stat label="Valid px" value={c.acquisition.dopWindow.validPixels.toLocaleString("en-US")} />
          </div>
        </Section>

        {/* COVERAGE */}
        <Section title="Coverage">
          <p className="font-body-sm text-[12px] text-on-surface-variant m-0">{c.coverageNote}</p>
        </Section>

        {/* TERRAIN */}
        <TerrainPanel terrain={c.terrain} terrainImage={c.images.terrain} />

        {/* ML */}
        <MlPanel ml={c.ml} />

        {/* FINAL INTERPRETATION */}
        <div className="bg-surface-container-high/60 tech-border rounded p-4">
          <h3 className="font-h2 text-h2 text-on-surface uppercase tracking-tight mb-2">
            Final Interpretation
          </h3>
          <p className="font-body-md text-body-md text-on-surface m-0">{c.finalInterpretation}</p>
        </div>
      </div>
    </main>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-surface-container-lowest tech-border rounded p-4">
      <h3 className="font-h2 text-h2 text-on-surface uppercase tracking-tight mb-2">{title}</h3>
      {children}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-surface-container-low tech-border rounded-sm p-2 text-center">
      <div className="text-outline uppercase text-[10px] tracking-wider">{label}</div>
      <div className="font-data-md text-data-md font-semibold mono-nums text-on-surface">{value}</div>
    </div>
  );
}
