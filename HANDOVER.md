# Handover

**As of:** 2026-08-26. **Branch:** `claude/continue-previous-work-ftb9l5` (PR
[#1](https://github.com/arsiwalamoiz24/SIH-26-internal-round/pull/1), open, head `87c90c6`).
Working tree clean, everything pushed.

This file is **not** another project explainer — `README.md` indexes those. It covers what a
person taking over cannot work out from the repo alone: what is blocked and on whom, which
source documents live outside the repo, and the mistakes this project has already made more
than once.

---

## Read in this order

1. `README.md` — index and layout.
2. `DECISIONS.md` — last three sections first. They cover the two most recent findings and
   supersede earlier conclusions in the same file.
3. `PRISM/docs/SINHA_SUPPLEMENTARY_FINDINGS.md` — the newest primary-source analysis. It
   overturns conclusions committed one day earlier; read it before trusting anything about
   CPR or DOP.
4. `PRISM/TODO.md` — open questions, several now resolved with pointers.

---

## The one thing to get right

**CPR agreement does not mean PRISM detects ice.**

PRISM's CPR reproduces Sinha et al. 2026's published numbers on their own confirmed-ice
craters (F2: 44.75% vs 47%; F3: 33.3% vs 42%). That is real, and it is the strongest
external validation this project has — **of the radar processing and crater geolocation.**

It is *not* evidence of ice. The paper's Supplementary Figure 6 reports rough terrain
outside F2 at mean CPR 1.1 with mean DOP 0.17, and states plainly that high CPR alone is
insufficient — the combined CPR–DOP criterion is what separates roughness-driven from
subsurface volumetric scattering. **Any ranking built on CPR alone ranks rough terrain and
subsurface ice identically.**

For roughly one day this repo said the opposite ("use CPR as the validated ground-truth
metric, de-emphasize DOP"). That was propagated into the frontend and several docs in
commit `d3ce772`, then withdrawn in `87c90c6`. If you find that wording anywhere it was
missed, it is wrong — correct it.

PRISM's DOP, meanwhile, is ~6× the paper's reported value and **unreconciled**. It is an
open problem blocking a complete criterion, not a metric to set aside.

---

## Blocked work, and who can unblock it

| # | Work | Blocked on | Who can unblock |
|---|---|---|---|
| 1 | `PRISM/src/nine_crater_validation_pipeline.py` | lat/lon + diameter for **F1, H1, H2, H3, S1, S2, S3, Tooley**. Only F2/F3 are transcribed. These are in the **main paper**, not the supplement. | anyone with the paper |
| 2 | Running *any* radar pipeline | The L4/L3C mosaics. Paths are hardcoded to `C:\Users\radhe\PRISM_local_data\...`; the team's Drive URL cache (`PRISM/data/raw/candidate_window_urls.json`) is gitignored and does not travel with the repo. | `rad117`, or whoever holds the Drive folder |
| 3 | Resolving DOP | Three untested avenues, see below. Needs #2. | — |
| 4 | Optical boulder detection | No labelled training data. BoulderNet was downloaded, verified, then rejected by the team and deleted. Imagery itself is solved (ShadowCam, verified for all 7 shortlisted candidates). | product decision |
| 5 | `Vercel – frontend` red check on every PR | A Vercel dashboard setting, not code — see below. | `rad117` |

### Item 1 is the highest-value open task

It is the first test in this project that can distinguish an ice signal from a roughness
signal. The design comes from the paper itself: nine doubly-shadowed craters (F1/F2/F3 in
Faustini, H1/H2/H3 in Haworth, S1/S2/S3 in Shoemaker), of which Supplementary Figure 5
annotates **F2, F3, H3, S1** as having relatively higher elevated-CPR pixel counts. All nine
are small, doubly shadowed, inside PSRs, same thermal environment, same morphological class
— so that 4-vs-5 split controls for sampling scale, shadowing and crater morphology *by
construction*, which no crater-catalogue control set achieves.

Fill the coordinates into `CRATERS`/`CONTROLS` and run it. The script **refuses to run on
placeholder coordinates** and prints exactly what is missing — do not defeat that guard. A
guessed coordinate produces a real-looking but meaningless validation result.

Note its stated limit: it tests **CPR ordering only**, because DOP needs Level-1A SLC
phase-preserving data and these are amplitude-derived mosaics. A positive result is
necessary-but-not-sufficient. Report it that way.

### Item 3 — the three DOP avenues

Hypotheses 1–8 are closed and **should not be re-run as they were**. But Supplementary
Table 1 arrived and reopened hypothesis 8: PRISM ran on *none* of the authors' six
acquisitions, so "wrong acquisition" is untested, not ruled out. What is genuinely new:

1. Run the DOP pipeline on the authors' own full-pol acquisitions (Supplementary Table 1,
   entries 2–6).
2. Compute **compact-pol / hybrid-basis** DOP on their compact-pol dataset
   `ch2_sar_ncls_20200808t201154198_d_cp_d18`, matching the m-χ formalism their own DOP
   citations point to. The investigation independently identified "different polarimetric
   basis" as the leading explanation *before* knowing they had a compact-pol dataset.
3. Apply Zhao et al. 2024's low-quality range-area removal (−30 dB antenna isolation) before
   computing DOP, and check whether the F2/F3 windows survive it. PRISM has never done this.

### Item 5 — the Vercel red check is not a code problem

From Vercel's own webhook payload: project `frontend` (rad117s-projects) has
`rootDirectory: null`, so it builds from the repo root, which has no `package.json` — that
build cannot succeed on any commit, including `main`. The sibling project `prism`
(moizs-projects) has `rootDirectory: "frontend"` and deploys the same commits fine.

Fix: set the `frontend` project's Root Directory to `frontend`, **or** delete/disconnect it
if `prism` is the intended deployment. Detail in
[PR #1 comment](https://github.com/arsiwalamoiz24/SIH-26-internal-round/pull/1#issuecomment-5421684174).
Do not spend time debugging the build — a clean checkout of `87c90c6` passes `npm ci` +
`npm run build` with all 12 routes.

---

## Source documents that are NOT in this repo

Five third-party PDFs were supplied by the team and used for the 2026-08-26 analysis. They
are copyrighted and deliberately not committed. Cite them by identifier; ask the team for
copies.

| Document | What it gave us |
|---|---|
| Sinha et al. 2026 **Supplementary Information** (`44453_2026_38_MOESM1_ESM.pdf`) | Supplementary Table 1 (their 6 acquisitions), Fig. 4–5 (the nine craters + control ROIs), Fig. 6 (CPR-alone-is-insufficient) |
| Chandrayaan-2 DFSAR **User Manual** (SAC/SIPG/MDPD/CH2/SAR/2020/12/23 v1.0) | Confirms **no vendor DOP/CPR/Stokes formula exists**; L1A SLI is complex, L2A SRI is amplitude-only |
| Zhao et al. 2024, IEEE TGRS 62:5208317 (full text) | Low-quality range-area removal → DOP hypothesis 9 |
| Ainsworth et al. 2006, IEEE TGRS 44(4):994–1003 | The crosstalk algorithm implemented in DOP hypothesis 7 |
| Xing et al. 2012, comment on Ainsworth 2006 | Documents a bug in the 2006 paper; noted, not silently patched |

**Still wanted:** the **main paper** (Sinha et al. 2026, npj Space Exploration 2:22,
doi:10.1038/s44453-026-00038-9) — specifically its crater table. That single table unblocks
item 1.

---

## Mistakes this project has already made — do not repeat them

Each of these actually happened and cost real time. They are documented in full in
`DECISIONS.md` and `PRISM/docs/CANDIDATE_ACQUISITION_SELECTION.md`.

1. **Bounding-box instead of point-in-polygon, near the pole. This has happened three
   times.** Footprints are rotated diagonals in polar-stereographic projection; an
   axis-aligned lat/lon box test says "covered" when the scene misses by kilometres. Always
   run a real point-in-polygon test against the product's own four corners, in the
   product's own CRS.
2. **Geolocation-correct is not the same claim as usable.** A NAC frame was verified as
   real, intact and correctly located — and was pure noise (adjacent-pixel correlation
   −0.077 vs 0.7–0.95 for real terrain). Check signal quality, not just integrity, before
   calling an acquisition a win.
3. **Whole-crater averaging destroys the ice signal.** Inside Faustini: 0.297 CPR over the
   whole 39 km disk, 0.567 in F2's neighbourhood, 0.967 in F2's interior. The signal lives
   in features ~0.08% the area of a whole-crater window. This is why the 2026-08-22
   independent validation returned a null result — read that document's headline finding
   together with the scale note in `DECISIONS.md`, never alone.
4. **`LDSM` is slope; `LDEM` is elevation.** A notebook read the pre-computed slope raster
   while believing it was elevation, making every downstream number meaningless. Caught only
   because printed "elevation" values exactly matched known slope statistics.
5. **Verify against the thing you actually changed.** A corrected UI panel was screenshotted
   against a stale dev server left running on an old port, and briefly looked like the fix
   had failed. Check what you are pointed at before concluding anything from it.

---

## Environment notes

- **Pipelines hardcode Windows paths** (`C:\Users\radhe\PRISM_local_data\...`). The newest
  script, `nine_crater_validation_pipeline.py`, accepts `PRISM_L4_DIR`, `PRISM_L3C_DIR` and
  `PRISM_REPO` environment overrides instead. Worth back-porting to the others.
- **If you are working in a Claude Code remote session:** outbound network may be restricted
  to package registries only. That blocks `/vsicurl/` reads against NASA PGDA and Google
  Drive, which several pipelines depend on. Check with
  `curl -sS "$HTTPS_PROXY/__agentproxy/status"` before assuming a download failure is real,
  and use an environment with open egress for data work.
- Frontend: `cd frontend && npm install && npm run dev`. Build is clean; `npm run lint`
  reports 5 pre-existing `no-explicit-any` errors in `lib/api.ts` and some `<img>` warnings —
  those predate this work and are not regressions.
- Python: `source venv/bin/activate` at repo root, then run `PRISM/src/*.py` directly.

---

## Suggested order of attack

1. Get the main paper's crater table → run `nine_crater_validation_pipeline.py`. This
   answers "does PRISM respond to ice, or just to roughness?", which everything else rests on.
2. Depending on that result, pursue the DOP avenues (item 3). DOP is required for a complete
   criterion regardless.
3. Fix or remove the `frontend` Vercel project so PRs stop showing a permanent red check.
4. Revisit the labelling approach for optical boulder detection (item 4) — imagery is ready,
   only labels are missing.
