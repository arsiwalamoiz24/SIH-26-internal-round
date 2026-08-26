# PRISM — TODO / Open Questions

Derived from the read-only audit in `PROJECT_STATUS.md` (2026-08-22). These are open items and questions to resolve with the project lead before any implementation work — this list is intentionally not a build plan.

## Immediate verification (blocks correct use of existing work)

- [x] **OHRC overlap check — RESOLVED by this audit, confirmed NOT overlapping.** The notebook's own XML print was truncated before the footprint block, so `ohrc.ipynb` never checked this itself. This audit read the full XML directly: scene corners are −89.22°…−89.93° latitude (a ≈22×2.6 km strip within ~24 km of the pole), while `SP_840980_0797630` is at −84.098° (≈179 km from the pole). **Do not use the current OHRC scene (`ch2_ohr_ncp_20251010T0942085687_d_img_d18`) for anything candidate-specific.** Open item: locate/acquire a different OHRC scene that actually covers −84.098°, 79.764°.
- [ ] Decide whether the corrupted `ch2_ohr_ncp_20230820T0559124374_d_img_n18_Bundle.tar` should be re-downloaded and its footprint checked — it may or may not be closer to the candidate; this was never determined since the bundle failed to open.
- [ ] **`obj2 (1).ipynb` cell 23 bug.** The `zip_path` points at the Y4R mosaic zip instead of the CPR/SERD/T-Ratio zip, so the notebook cannot currently reproduce its own displayed CPR/SERD numbers from a clean run. Confirm with whoever wrote it whether the displayed cells 26–29 output is trustworthy (i.e., from an earlier correct run) or should be discarded pending a re-run with the correct path.
- [ ] Confirm whether the LOLA DEM download in `obj2` cell 30 (`LDSM_80S_20MPP_ADJ.TIF`, `LDEM_80S_20MPP_ADJ.TIF`) was ever completed in the original Colab session (the saved notebook only shows it reaching 18%). If not, it needs to finish before cells 31–34 can produce any real output.
- [ ] Once the DEM is available, actually execute `obj2` cells 31–34 and capture the real slope crop / safe-caution-hazard percentages for `SP_840980_0797630` — these currently do not exist anywhere despite the code being written.
- [ ] Note: "slope" in `obj2` is read directly from NASA's pre-computed `LDSM` raster — there is no in-house slope algorithm. `LDEM` (elevation) is downloaded but never used. Decide whether to (a) keep relying on the NASA slope product, or (b) compute slope/roughness/TRI in-house from `LDEM` for more control and to add the roughness/elevation-variation metrics the brief asks for (neither exists today).

## Scientific questions for the project lead (not implementation)

> **DOP stop rule (2026-08-25):** the DOP items below marked RESOLVED were settled by an
> 8-hypothesis investigation covering every calibration, processing and acquisition-level
> avenue reachable from public sources. Do not re-open them — the only remaining productive
> step is obtaining Sinha et al.'s Supplementary Table 1 or contacting the authors.
> Full detail: `docs/DOP_GROUND_TRUTH_INVESTIGATION.md`.

- [x] **RESOLVED empirically (2026-08-25) — the formula is defensible, but it does not reproduce published values.** Is the DOP formula (general Stokes theory: `DOP = sqrt(S2²+S3²+S4²)/S1` from a 2×2 covariance of bias-corrected HH/VV) an acceptable stand-in? Tested directly against Sinha et al. 2026's own confirmed-ice craters: PRISM returns ~6× their reported 0.10–0.13, and 8 independently-tested hypotheses failed to close the gap. The formula is standard and the data is well-calibrated; the paper's DOP is most likely from a different processing level or polarimetric basis (their DOP-interpretation citations are hybrid/compact-pol, not quad-pol). See `docs/DOP_GROUND_TRUTH_INVESTIGATION.md`. **Consequence: CPR, not DOP, is PRISM's validated ground-truth criterion** — CPR does reproduce the paper on the same craters.
- [x] **RESOLVED — linear-pol covariance was the one extended.** It is now computed on real, footprint-confirmed, candidate-specific windows for 4 of the 7 shortlisted PSRs plus both of the paper's craters (F2/F3). The other two formulations remain as secondary cross-checks only. Note the ~0.08 spread between formulations turned out to be irrelevant next to the 6× gap against published values.
- [ ] The measured co/cross-pol phase offsets (50.3°/−5.0°) don't match the XML's `phase_orthogonality` values (−5.3°/3.1°/−3.4°/−1.1°) by roughly an order of magnitude — is this expected (different physical quantities being compared) or a bug in the notebook's channel/byte identification?
- [ ] The HH channel's std-dev/bias fit to the XML reference is the weakest of the four polarizations (§3.2 of the status doc) — worth double-checking the G0/G1/G2/G3 → HV/HH/VV/VH mapping before trusting HH-dependent results.
- [ ] SERD's large NaN fraction (flagged in `objective1_dfsar_validation.ipynb.ipynb`'s debug cell) — is this expected product behavior (e.g., masked low-coherence pixels) or a read/processing issue?
- [ ] Should the "high Pv" percentile-based tier (top decile of the current scene) be replaced or supplemented with an absolute/literature-derived ice-relevant Pv threshold?
- [x] **RESOLVED — done, and then some.** DOP is now computed on a window centered on `SP_840980_0797630` from a footprint-confirmed covering acquisition (`ch2_sar_ncxl_20220318t135736694_d_fp_d18`), plus 3 further shortlisted candidates (`outputs/objective1/dop_secondary/`) and both of the paper's F2/F3 craters. The arbitrary early-slice patch is no longer used for anything candidate-specific. Acquisition selection method: `docs/CANDIDATE_ACQUISITION_SELECTION.md`.
- [ ] Confirm the slope hazard thresholds (<10° safe / 10–20° caution / >20° hazard) — the notebook author already flagged these as "crude"; what is the actual mission-relevant threshold source (rover specs? lander specs?) before these are used for any real go/no-go decision?

## Housekeeping

- [ ] Rename or remove `OHRC data analysis(pure Physiscs).ipynb` — it is a byte-identical duplicate of `objective1_y4r_polarimetry.ipynb.ipynb` and contains no OHRC content. Decide whether this was an accidental save-as (in which case it can likely be deleted) or whether real OHRC-physics work was lost and needs to be redone.
- [ ] Minor: `objective1_y4r_polarimetry.ipynb.ipynb` and `objective1_dfsar_validation.ipynb.ipynb` both have a doubled `.ipynb.ipynb` extension, and `OHRC data analysis(pure Physiscs).ipynb` has a typo ("Physiscs"). Cosmetic, but worth a clean rename pass.
- [ ] All notebooks use hard-coded Colab (`/content/drive/MyDrive/...`) paths — none are portable outside the original author's Google Drive. Worth deciding on a shared data convention before other people try to run these.
- [ ] None of the 5 notebooks contain markdown cells — no in-notebook documentation of purpose/assumptions exists. Consider adding minimal markdown headers, at least to the notebooks being kept, so intent doesn't have to be re-derived from code every time.
- [ ] `PRISM/data`, `PRISM/doc`, `PRISM/outputs`, `PRISM/src`, `PRISM/tests` are all currently empty — confirm whether that's expected at this stage or whether content is missing from this repo checkout.

## Explicitly NOT to do yet (per audit brief)

- Do not compute DOP from Y4R EVN/VOL/ODD/HLX components (current notebooks already correctly avoid this — keep it that way unless someone provides a scientific justification).
- Do not treat the current 25×1024-pixel DOP patch as representative of `SP_840980_0797630` or any specific PSR.
- Do not force the current OHRC scene into candidate-specific analysis before the overlap question above is answered.
- Do not present the `obj2` slope thresholds as validated mission thresholds.
- Do not build a supervised ice-classifier CNN — no ground-truth labels exist.
- Do not claim Isolation Forest / YOLOv8 / ML anomaly detection is "implemented" — it does not exist in the codebase yet.
