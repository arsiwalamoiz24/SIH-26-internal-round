import Link from "next/link";

/**
 * Drop-in honesty banner for pages built before the real-pipeline data connection.
 * Use on pages/sections where most values are reference/placeholder content that has
 * not been derived from the validated PRISM physics pipeline for this candidate.
 */
export function IllustrativeBanner({ detail }: { detail: string }) {
  return (
    <div className="bg-amber-50 border border-amber-300 rounded px-3 py-2 flex items-start gap-2 text-[11px] font-body-sm text-amber-900">
      <span className="material-symbols-outlined text-amber-600 text-[16px] shrink-0">warning</span>
      <p className="m-0 leading-snug">
        <strong className="uppercase tracking-wide">Illustrative / Reference Content —</strong>{" "}
        {detail} See the verified{" "}
        <Link href="/candidate/SP_840980_0797630" className="underline font-semibold">
          candidate report
        </Link>{" "}
        for real pipeline results.
      </p>
    </div>
  );
}
