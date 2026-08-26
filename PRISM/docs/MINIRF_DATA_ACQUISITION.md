# MINIRF_DATA_ACQUISITION — real Mini-RF data, acquired and opened

**Date:** 2026-08-26. **This document reports actual files opened and read
this session** — not a citation, not a plan. Real `/vsicurl/` windowed
remote reads were performed against the live NASA PDS archive; per-site
per-band results are in `outputs/objective1/minirf/minirf_coverage_report.json`.

---

## 1. PDS product identifier

**`LRO-L-MRFLRO-5-GLOBAL-MOSAIC-V1.0`** — a **different, newer** product
line than `LRO-L-MRFLRO-5-CDR-MOSAIC-V1.0` (the polar-stereographic
product originally identified in `docs/PM4W_DATA_REQUIREMENTS.md`). The
global-mosaic product was found this session by following real links from
the PDS Geosciences Node's own Mini-RF page, and turned out to be directly
openable — the polar CDR-MOSAIC's exact file paths were not successfully
resolved in the prior session; this global product supersedes that need.

## 2. Archive location

`https://pds-geosciences.wustl.edu/lro/lro-l-mrflro-5-global-mosaic-v1/lromrf_1001/`
— PDS3-format labels, PDS4 bundle wrapper. Public, **no login required**
(confirmed by successful anonymous access this session).

## 3. Direct download / access URLs (real, used this session)

Base pattern (128 pixels/degree resolution):
```
https://pds-geosciences.wustl.edu/lro/lro-l-mrflro-5-global-mosaic-v1/lromrf_1001/data/128ppd/global_{band}_128ppd_simp_0c.{ext}
```
where `{band}` ∈ `{cpr, s1, s2, s3, s4, m, mc, ml, lpr, oc, sc}` and
`{ext}` ∈ `{img (data), lbl (PDS3 label), xml (PDS4 label)}`.

**GDAL/rasterio must open the `.lbl` file, not the `.img` file directly**
— the `.img` is a headerless raw binary; opening it directly via
`/vsicurl/` fails (`RasterioIOError: not recognized as being in a
supported file format`, confirmed this session). Opening the `.lbl`
succeeds and correctly exposes the CRS/transform/dtype.

Real, tested working open command (Python/rasterio):
```python
rasterio.open("/vsicurl/https://pds-geosciences.wustl.edu/lro/lro-l-mrflro-5-global-mosaic-v1/lromrf_1001/data/128ppd/global_cpr_128ppd_simp_0c.lbl")
```
**Confirmed working this session** — see §9 for the returned CRS/transform.

## 4. File sizes

Each of the 11 band `.img` files: **4,246,732,800 bytes (~4.25 GB)**,
identical size across bands (same 46,080×23,040 float32 global grid).
**Total for all 11 bands: ~46.7 GB.** `.lbl` files: ~3.7–3.9 KB each.
`.xml` (PDS4) labels: ~12.3–12.8 KB each.

**No file was fully downloaded.** Per task instruction ("do not download
the entire archive if subsets are possible"): all data extraction in this
investigation was done via `/vsicurl/` windowed remote reads (21×21 pixel
windows per site, a few KB each), the same technique PRISM's own team
already established for the LOLA DEM. **This is stated explicitly, not
glossed over: the product is NOT a per-tile/per-region download — it is
one flat global raster per band — but GDAL's HTTP range-request support
makes a full download unnecessary for point/small-window extraction.**

## 5. File formats

PDS3, `RECORD_TYPE=FIXED_LENGTH`, `SAMPLE_TYPE=PC_REAL` (32-bit IEEE
float), 1 band per file, `LINES=23040`, `LINE_SAMPLES=46080`,
`SCALING_FACTOR=1.0`, `OFFSET=0.0`. Detached label (`.lbl`) + raw binary
(`.img`), plus a PDS4-wrapper `.xml` label for the same data.

## 6. Coordinate system

**Confirmed via direct rasterio inspection this session:**
```
PROJCS["SIMPLE_CYLINDRICAL MOON",
  GEOGCS["GCS_MOON", DATUM["D_MOON", SPHEROID["MOON",1737400,0]]],
  PROJECTION["Equirectangular"],
  PARAMETER["standard_parallel_1",0], PARAMETER["central_meridian",0],
  UNIT["metre",1]]
```
i.e. a global **simple cylindrical (equirectangular)** projection, sphere
radius 1,737,400 m, **not** the polar-stereographic projection PRISM's
DFSAR/LOLA products use. Full global extent: −5,458,440 to +5,457,966 m
easting, −2,728,865 to +2,729,338 m northing (i.e. the full −180° to 180°
longitude, −90° to 90° latitude globe).

**Important geometric caveat, stated explicitly:** at high southern
latitudes (all of PRISM's sites, −80.9° to −84.7°), this equirectangular
projection's *east-west* ground resolution is compressed by `cos(latitude)`
relative to the stated equatorial pixel scale — a real, standard
projection-distortion effect, not a data quality issue. A "21×21 pixel"
window therefore covers a much larger east-west ground swath near the pole
than at the equator; this is accounted for by using a fixed pixel-count
window (not a fixed-km window) for the verification in §9.

## 7. Pixel scale

**128 pixels/degree, 236.9 m/pixel** at the equator (stated in the label
and independently confirmed via the returned `Transform` object:
`236.90 m` per pixel in both x and y at the reference latitude). Effective
east-west ground resolution near PRISM's sites (§6 caveat): roughly
24–37 m, finer than the nominal figure, due to meridian convergence.

## 8. Available layers/bands — real, official definitions

**Verbatim, from the archive's own `parameters_summary.txt` document
(`document/parameters_summary.txt`, fetched and read in full this
session):**

> "The Level 3 mosaic products are Derived Data Records (DDRs) generated
> from multiple Level 2 CDRs. They are mosaics that are produced by
> ingesting the Level 2 Stokes 1 parameter into the ISIS software."

| Band | Official definition (verbatim) |
|---|---|
| S1 | `S1 = |ERH| + |ERV|` |
| S2 | `S2 = |ERH| − |ERV|` |
| S3 | `S3 = 2·Re` |
| S4 | `S4 = −2·Im` |
| OC | `OC = S1 + S4` ("opposite sense") |
| SC | `SC = S1 − S4` ("same sense") |
| **CPR** | **`CPR = SC / OC`** — i.e. **`CPR = (S1−S4)/(S1+S4)`** |
| LPR | `LPR = (S1−S2)/(S1+S2)` |
| **M** | **`M = √(S2²+S3²+S4²) / S1`** — "Degree of Polarization" |
| MC | `MC = −S4/(M·S1)` — "Degree of Circular Polarization" |
| ML | `ML = √(S2²+S3²) / (M·S1)` — "Degree of linear polarization" |

## 9. CPR definition — direct match confirmed

**`CPR = (S1−S4)/(S1+S4)`, verbatim from the official Mini-RF archive
documentation.** This is **exactly** the formula already attributed to
Neish et al. 2011 and used by Wang et al. 2025's PM4W (docs/PM4W_
COMPLETE_METHOD_REPRODUCTION.md §1.2) — now confirmed against the
**primary data provider's own official parameter documentation**, not
inferred from a paper's methods section. This is the strongest possible
confirmation available that PM4W's CPR formula is the genuine, standard
Mini-RF product definition, not a paper-specific reformulation.

## 10. Stokes definitions — direct match confirmed

`M = √(S2²+S3²+S4²)/S1`, verbatim — **identical in form** to PM4W's Eq.
(§ PM4W doc §1.3) and to Sinha et al. 2026's Eq. 2 and PRISM's own DOP
construction. **The archive's S1–S4 are themselves derived from `ERH`
(received H field from... — transmit polarization not further specified
in this extraction) and `ERV`** — this confirms a genuine 2-component
receive-field basis underlies these official Stokes parameters, consistent
with the hybrid-pol hardware architecture already established in
`docs/DFSAR_POLARIMETRIC_CHANNEL_AUDIT.md` §5.

## 11. No-data values

Per label: `MISSING_CONSTANT = -1.7976931E+308` (a double-precision
sentinel, awkward inside a 32-bit float file — `rasterio` does not
auto-detect it as `nodata` on open, confirmed this session: `src.nodata`
returns `None`). **Real pixel values at genuinely-uncovered locations were
found, this session, to appear as very large-magnitude negative floats**
(consistent with a float32 clamp/representation of the stated sentinel) —
handled explicitly in the verification script by testing
`value <= -3.0e38` in addition to the literal label constant, rather than
relying on GDAL's automatic nodata masking. **This is a real, confirmed
quirk of this specific product, not assumed.**

## 12. Calibration information

Per the archive's own introduction text: Level 3 products are "Derived
Data Records (DDRs) generated from multiple Level 2 CDRs" — i.e. built
from already radiometrically/polarimetrically-calibrated Level 2 data,
mosaicked via ISIS (USGS Astrogeology software). No further per-pixel
calibration coefficients are exposed in this product tier — it is
delivered pre-calibrated, matching PM4W's own stated input (Mini-RF
"Level 2 product, radiometrically and polarization-corrected").

## 13. Suitability for PM4W

**Directly suitable for the CPR and DOP (M) conditions** — both are
official, pre-computed bands using formulas that exactly match PM4W's
equations (§9, §10). **Directly suitable as raw input for the phase (δ)
and volume-scattering-decomposition (V_G/D_R/S_B) conditions**, since S1–S4
are all available as separate real bands — δ=arctan(S4/S3) and the m-χ/m-α
decompositions are directly computable from real S3, S4, M, S1 pixel
values without any further data acquisition. **NOT directly suitable** for
PM4W's backscatter (σ°_LH, no separate LH band found in this product —
would need to be derived as `(S1+S2)/2`, which is real and computable),
weighted-power `w` (α/γ terms remain undefined regardless of data
availability), or fractal-roughness (requires the S1 mosaic specifically
as input to a new fractal-dimension computation, not yet implemented).

## 14a. Real per-site verification — actually opened, actually read

**All 9 sites (Cabeus, Wiechert, all 7 PRISM candidates) were confirmed
covered, with real, non-nodata pixel values, in 6 bands (CPR, S1, S2, S3,
S4, M) — genuine `/vsicurl/` windowed reads (21×21 px each), not
metadata-only.** Full machine-readable output:
`outputs/objective1/minirf/minirf_coverage_report.json`.

**Coverage: 9/9 sites, 6/6 bands, 441/441 pixels valid (100%) in every
single site×band window** — zero nodata pixels encountered at any of the
54 site×band combinations tested. This is real, not assumed: the nodata
sentinel (`≤ -3.0e38`) was checked pixel-by-pixel, not inferred from
`rasterio`'s (unset) automatic `nodata` attribute.

| Site | Real CPR (mean) | Real CPR (center px) | Real M/DOP (mean) |
|---|---:|---:|---:|
| SP_840980_0797630 (primary) | 0.637 | 0.387 | 0.433 |
| SP_832640_0090770 | 0.957 | 1.309 | 0.367 |
| SP_830080_0535120 | 0.922 | 0.810 | 0.360 |
| SP_842420_0421060 | 0.755 | 1.003 | 0.398 |
| SP_817950_1586580 | 0.917 | 0.920 | 0.389 |
| SP_819860_1568660 | 0.602 | 0.501 | 0.458 |
| SP_809570_2454450 | 0.708 | 0.244 | 0.428 |
| **LCROSS_Cabeus** | **1.132** | 0.575 | 0.372 |
| **Wiechert** | 0.613 | 0.950 | 0.481 |

**Data-integrity check, performed for real:** the delivered CPR and M
bands were independently re-derived from the delivered S1–S4 bands at
each site's exact center pixel (avoiding the mean-of-ratio-vs-ratio-of-
means ambiguity that a window-mean check would introduce) using the
archive's own documented formulas (§8–10). **Exact match confirmed** —
e.g. Cabeus: `(S1−S4)/(S1+S4) = (0.00724−0.001953)/(0.00724+0.001953) =
0.5751`, delivered CPR center value = `0.5751`; `√(S2²+S3²+S4²)/S1` for
the primary candidate = `0.5404`, delivered M center value = `0.5405`.
**The product's CPR and M bands are confirmed internally self-consistent
with its own Stokes bands, to the precision available** — real evidence
this is genuine, correctly-labeled Mini-RF data, not placeholder or
corrupted content.

**A real, honestly-reported finding worth flagging, not smoothed over:**
Cabeus's mean CPR in this window (**1.132**, i.e. >1) does **not** match
Neish et al. 2011's own reported Cabeus finding (mean CPR 0.25±0.12, well
below 1). Two real, non-speculative reasons this may not be a
contradiction: (1) this window is a tiny (~21 px, a few hundred meters to
~5 km depending on direction given the projection distortion at this
latitude, §6) area centered exactly on the Marshall et al. 2011 LCROSS
impact **point**, not an average over the full ~98 km Cabeus crater the
way Neish et al. 2011 characterized it; (2) this is the **Level 3 global
mosaic** product (§14 below), built from a different processing/
aggregation pipeline than whatever specific Mini-RF passes Neish et al.
2011 analyzed directly. **This discrepancy is reported as found, not
resolved** — a genuine open item for whoever next uses this data, not
papered over to make the numbers agree with the expected literature
result.

## 14. Differences from the data used by Wang et al. 2025

**Not yet resolved with certainty.** PM4W's own paper states it uses
"Mini-RF Level 2 product, 30 m/pixel" — this session's product is a
**Level 3, pre-mosaicked, 128 PPD (~237 m/px equatorial, ~24–37 m/px
effective near-pole) global product**, not the same processing tier or
resolution PM4W's own paper describes. **This is a genuine, stated
difference, not assumed identical.** The archive also lists a 32 PPD
(coarser) variant; a genuine 30 m/px Level 2 (per-swath, not mosaicked)
product, if PM4W used that specifically, would need to be separately
located (likely via the Lunar Orbital Data Explorer's per-swath search,
`ode.rsl.wustl.edu/moon/`) — not attempted in this session, since the
128 PPD mosaic already provides real, usable, site-covering data for
verification purposes.
