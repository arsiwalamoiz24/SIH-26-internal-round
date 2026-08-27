# MINIRF_CABEUS_CPR_RECONCILIATION — Neish 2011 vs. this session's real extraction

**Date:** 2026-08-26. **Do not read this as "Neish is wrong" or "the new
product is wrong"** — the evidence assembled here shows both are correct,
internally consistent characterizations of the same real surface at two
genuinely different spatial scales, one of which sits on a documented,
independently-confirmed, non-ice geological feature.

---

## The discrepancy, stated precisely

- **Neish et al. (2011)**, full text obtained (JGR Planets 116, E01005,
  DOI 10.1029/2010JE003647): Cabeus crater-wide mean CPR = **0.38±0.23**
  (LRO Mini-RF) / **0.25±0.12** (Chandrayaan-1 Forerunner) — both below 1,
  both near/below the south-polar regional average.
- **This session's real extraction** (LRO-L-MRFLRO-5-GLOBAL-MOSAIC-V1.0,
  genuine `/vsicurl/` pixel reads at the Marshall et al. 2011 LCROSS impact
  coordinate, −84.6796°, −48.7093°): a 21×21-pixel window gives **mean CPR
  = 1.13**; a 61×61-pixel window gives **mean CPR = 1.09, with 46.2% of
  pixels individually exceeding CPR>1** — the highest CPR>1 fraction of
  all 9 sites tested in this entire investigation.

## 1. What exact product did Neish et al. 2011 use?

**Two calibrated mosaics, not raw/single-pass data** (verbatim/paraphrased
from full text): Chandrayaan-1 Forerunner (150 m resolution, Feb–Apr 2009)
and LRO Mini-RF (30 m "zoom" mode, processed to 15 m, then **mosaicked at
50 m pixel size**). Both **monostatic S-band, 12.6 cm** — same frequency
as the global mosaic product this session used, confirmed no bistatic
X-band involved in Neish's Cabeus analysis specifically. Statistics were
**crater-wide means over the entire ~98 km Cabeus crater**, with no floor/
wall/rim subdivision.

## 2. Incidence angle / geometry

Chandrayaan-1 look angle 32°; LRO look angle 48°. Both near-polar,
side-looking. **Verbatim, on within-crater heterogeneity:** *"There is
also no noticeable change in CPR between the illuminated portion of the
crater and the shadowed portion."* **However — and this is the decisive
clue — Neish et al. 2011 themselves already identify a real, small,
localized anomaly:** *"a radar bright spot"* near the impact site, which
they caution *"may simply represent a preexisting boulder or impact
crater."* **This means Neish et al. 2011's own paper already flags the
existence of exactly the kind of feature this session's small window
turned out to sample** — not a contradiction discovered here for the first
time, but confirmation the authors were aware such small-scale features
exist within their crater-wide average.

## 3. Product version / reprocessing

No evidence found of a Mini-RF instrument recalibration between 2011 and
this session's global-mosaic product. The `.img` files carry internal
processing dates around 2012; the PDS4 XML wrapper labels are dated 2024,
but this most plausibly reflects a metadata/archival wrapper update, not a
radiometric reprocessing — **not independently confirmed either way,
flagged AMBIGUOUS**, not ruled out.

## 4. The decisive finding — a real, independently published 2024 study

**Fassett et al. (2024), *Geophysical Research Letters*, "The LCROSS
Impact Crater as Seen by ShadowCam and Mini-RF: Size, Context, and
Excavation of Copernican Volatiles," DOI 10.1029/2024GL110355** — full
text obtained this session, directly on-topic, resolves the discrepancy:

- The actual LCROSS Centaur impact crater has now been precisely
  identified: **~22 m diameter, at −84.6780°, −48.6926°** — a small, real
  refinement (roughly a few hundred meters) from Marshall et al. 2011's
  pre-impact estimate (−84.6796°, −48.7093°, the coordinate this session
  used).
- **Verbatim: "The LCROSS crater formed directly on top of an ejecta ray
  visible in Mini-RF from [a] pre-existing 900-m diameter crater... this
  ray extends >2 crater radii from the source crater and... is
  radar-bright, suggest[ing] it is young (<~500 Myr)."**
- **Verbatim: the fresh LCROSS crater itself shows "a significant new
  local maximum that was ~4 dB (2.5×) higher in total backscattered
  power" than surrounding terrain, extending to ~50 m from the crater
  center.**

**This is the exact, well-documented, independently-published
fresh-crater-ejecta CPR/backscatter-enhancement mechanism already
established elsewhere in this investigation** (Carter et al. 2012:
wavelength-scale roughness and double-bounce geometry from young ejecta
elevate CPR — a real, non-ice cause). The coordinate this session sampled
sits within roughly 50 m of a documented, radiometrically-confirmed,
non-ice radar-bright feature.

## 5. Is the sampled window representative of Neish's crater-wide statistic?

**No — real evidence shows it is a small, documented, localized feature,
not representative of the crater-wide average.** A 98-km-wide crater
diluting a ~50–100 m-scale local anomaly across its full area would
produce almost no trace of it in a crater-wide mean — exactly consistent
with Neish et al. 2011's own low reported average, and exactly consistent
with their own "radar bright spot... may represent a preexisting boulder
or impact crater" caveat.

## Most likely explanation(s), ranked by evidentiary support

1. **(Strongly supported, real evidence) Scale and location mismatch,
   compounded by a real, independently-documented local anomaly.** This
   session's small window sits almost exactly on a confirmed young-crater
   ejecta ray with a documented +4 dB backscatter enhancement. Neish et
   al. 2011's crater-wide average correctly dilutes this small feature to
   near-invisibility. **The two measurements are not in conflict — they
   characterize different spatial scales of the same real surface, and
   both are physically consistent with known, non-ice radar mechanisms.**
2. **(Weakly supported, real but minor) Coordinate refinement.** The exact
   point sampled differs from the now-precisely-known crater location by
   a few hundred meters — small relative to the pixel window used, but a
   real, quantified effect.
3. **(Not supported by evidence found, genuinely unresolved) Product-
   version/calibration mismatch.** No specific recalibration event was
   found; the 2024 XML wrapper date most plausibly reflects metadata, not
   new radiometric processing — flagged AMBIGUOUS, not ruled out, since it
   was not independently confirmed either way.

## What this means for this investigation's PM4W results

Cabeus's real, elevated CPR (mean 1.09, 46.2% of pixels >1) found in
`docs/PM4W_VALIDATION_RESULTS.md` **should not be read as evidence of
ice** on its own — the specific coordinate sampled is now understood, via
independent 2024 literature, to sit on a documented fresh-crater ejecta
feature. This is precisely the "high CPR from roughness, not ice"
mechanism this entire investigation (Neish 2011, Carter 2012, Eke 2014, Fa
2018) has repeatedly found to be a real, non-hypothetical confound — now
confirmed, concretely and specifically, at the exact location this
investigation sampled. Cabeus's real, decisive PM4W `NON_ICE`
classification (driven primarily by its low DOP pass rate — only 11.9% of
pixels — not by CPR at all) is **not** contradicted by this finding; if
anything, the ejecta-ray explanation for Cabeus's *elevated CPR* removes
what would otherwise have been the strongest counter-argument against that
classification.
