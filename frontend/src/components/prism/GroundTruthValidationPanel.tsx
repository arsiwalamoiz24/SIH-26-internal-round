import type { PaperGroundTruthValidation } from "@/lib/api";

/**
 * External ground-truth check against Sinha et al. 2026 -- PRISM's own pipeline
 * run on the paper's own confirmed-ice craters (F2/F3, Faustini).
 *
 * Deliberately shows both halves of the result. CPR reproduces the paper's
 * published numbers, which is the project's strongest external validation;
 * DOP does not, across 8 independently-tested hypotheses, and that mismatch
 * is presented at the same weight rather than buried under the match.
 */
export function GroundTruthValidationPanel({ v }: { v: PaperGroundTruthValidation }) {
  const s = v.shortlistAgainstCriterion;

  return (
    <div className="bento-card mx-1 flex flex-col overflow-hidden shrink-0">
      <div className="bento-header shrink-0">
        <h3 className="font-data-md text-data-md text-on-surface m-0 uppercase text-[11px] tracking-wider">
          Published Ground Truth (Sinha et al. 2026)
        </h3>
        <span className="text-[9px] font-mono text-tertiary bg-surface-container px-1.5 py-0.5 rounded border tech-border uppercase font-bold">
          REAL PIPELINE
        </span>
      </div>

      <div className="p-3 flex flex-col gap-3 font-mono text-[11px]">
        <p className="text-[10px] text-on-surface-variant leading-relaxed m-0">
          PRISM&apos;s pipeline run on the paper&apos;s <strong>own confirmed-ice craters</strong> (F2, F3
          inside Faustini), compared against the paper&apos;s published values.
        </p>

        {/* CPR — validated */}
        <div className="rounded border border-outline-variant bg-surface-container-low overflow-hidden">
          <div className="flex justify-between items-center px-2 py-1.5 border-b border-outline-variant">
            <span className="text-on-surface font-bold uppercase tracking-wide text-[10px]">
              CPR &gt; 1 criterion
            </span>
            <span className="text-[#10b981] font-bold uppercase text-[10px]">{v.cpr.verdict}</span>
          </div>
          <table className="w-full text-[10px]">
            <thead>
              <tr className="text-outline">
                <th className="text-left font-normal px-2 py-1">Crater</th>
                <th className="text-right font-normal px-2 py-1">PRISM %&gt;1</th>
                <th className="text-right font-normal px-2 py-1">Paper %&gt;1</th>
                <th className="text-right font-normal px-2 py-1">PRISM max</th>
                <th className="text-right font-normal px-2 py-1">Paper max</th>
              </tr>
            </thead>
            <tbody>
              {v.cpr.craters.map((c) => (
                <tr key={c.id} className="border-t border-outline-variant/60">
                  <td className="px-2 py-1 text-on-surface font-semibold">
                    {c.id}
                    <span className="text-outline font-normal"> · {c.paperVerdict}</span>
                  </td>
                  <td className="px-2 py-1 text-right text-primary font-bold mono-nums">
                    {c.prismPctGt1.toFixed(1)}%
                  </td>
                  <td className="px-2 py-1 text-right text-on-surface-variant mono-nums">
                    {c.paperPctGt1}%
                  </td>
                  <td className="px-2 py-1 text-right text-primary font-bold mono-nums">
                    {c.prismMax.toFixed(2)}
                  </td>
                  <td className="px-2 py-1 text-right text-on-surface-variant mono-nums">
                    {c.paperMax.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* DOP — not reconciled */}
        <div className="rounded border border-outline-variant bg-surface-container-low overflow-hidden">
          <div className="flex justify-between items-center px-2 py-1.5 border-b border-outline-variant">
            <span className="text-on-surface font-bold uppercase tracking-wide text-[10px]">
              DOP &lt; 0.13 criterion
            </span>
            <span className="text-error font-bold uppercase text-[10px]">{v.dop.verdict}</span>
          </div>
          <div className="px-2 py-1.5 flex justify-between items-center text-[10px] border-b border-outline-variant/60">
            <span className="text-on-surface-variant">
              PRISM F2 / F3 (same craters, same data)
            </span>
            <span className="text-on-surface font-bold mono-nums">
              {v.dop.prismF2Mean.toFixed(2)} / {v.dop.prismF3Mean.toFixed(2)}
              <span className="text-outline font-normal">
                {" "}
                vs {v.dop.paperRange[0].toFixed(2)}&ndash;{v.dop.paperRange[1].toFixed(2)}
              </span>
            </span>
          </div>
          <p className="text-[9px] text-on-surface-variant leading-relaxed m-0 px-2 py-1.5">
            {v.dop.hypothesesTested} independent hypotheses &mdash; window size, small-sample bias,
            absolute and relative calibration, Zhao 2024 multilook, self-derived crosstalk, the full
            Ainsworth 2006 crosstalk algorithm, and a completely independent covering acquisition
            &mdash; were each tested to completion. None closed the gap.
          </p>
        </div>

        {/* Shortlist against the criterion */}
        <div className="flex justify-between items-center p-2 bg-surface-container-low rounded border border-outline-variant">
          <span className="text-on-surface-variant">Shortlist meeting FULL criterion</span>
          <span className="text-on-surface font-bold mono-nums">
            {s.meetFullCriterion} of {s.candidatesEvaluated}
            <span className="text-outline font-normal"> (DOP real for {s.dopComputedFor})</span>
          </span>
        </div>

        <p className="text-[9px] text-outline leading-relaxed m-0">
          <strong>Reading this honestly:</strong> the CPR agreement is real external validation that
          PRISM&apos;s radar processing and crater geolocation are correct. The DOP gap is equally real
          and unexplained &mdash; so DOP is reported as a measurement, not as validated evidence, and
          CPR is the criterion PRISM ranks on. The paper&apos;s craters are also 700&ndash;3000 m
          sub-features while PRISM&apos;s candidates are PSR-scale polygons, so applying the threshold
          at PSR scale is an extrapolation. Full detail: <code>{v.doc}</code>.
        </p>
      </div>
    </div>
  );
}
