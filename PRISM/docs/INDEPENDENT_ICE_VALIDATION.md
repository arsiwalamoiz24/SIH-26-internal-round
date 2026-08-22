# INDEPENDENT_ICE_VALIDATION — PRISM vs. independently-sourced ice references

**Date:** 2026-08-22

**Headline finding, stated up front, not buried:** in this validation set, PRISM's radar evidence score (Pv/CPR/T-Ratio composite) does **NOT** systematically separate independently-identified ice-reference sites from checked-negative controls. Positive sites and controls are interleaved throughout the ranking, and the single highest-confidence reference (LCROSS Cabeus, a direct in-situ measurement) scores **lowest of all 11 tested sites**. This is reported as found — nothing below was adjusted, re-weighted, or re-run to change this outcome.

---

## Definitions used throughout this document

- **Independently confirmed ice**: LCROSS Cabeus only — a direct, in-situ physical/spectroscopic measurement of water in impact ejecta (Colaprete et al. 2010), not a remote inference.
- **Independent ice evidence** (weaker than "confirmed"): the 7 M3-positive craters from Li et al. 2018 — a remote spectral inference, crater-level, from a criterion that itself has a published scientific critique (see §2).
- **Control / no reported ice evidence**: the 5 craters Li et al. 2018 explicitly checked (Diviner cold traps, Tmax ≤110K) and explicitly reported as **not** showing an ice absorption feature — not merely "unstudied" locations.
- **PRISM prediction**: PRISM's own Pv/CPR/SERD/T-Ratio window statistics and the physics-evidence-score analog computed in this task, kept strictly separate from the three categories above (PRISM outputs were never used as labels).

---

## TASK 1 — Machine-readable ice-reference dataset search

**Result: the M3 pixel-level ice-detection dataset is INSUFFICIENT for quantitative pixel-level validation — confirmed by direct inspection, not assumed.**

- Searched for Li, S. et al. (2018), "Direct evidence of surface exposed water ice in the lunar polar regions," *PNAS* 115(36):8907-8912, doi:10.1073/pnas.1802345115 — the primary M3 south-polar ice-detection publication.
- Downloaded the paper's actual SI Appendix PDF this session (via Europe PMC's supplementary-files endpoint, 17.7 MB zip, 9 files) — saved at `outputs/validation/refs/pnas.1802345115.sapp.pdf` (20.25 MB, 23 pages) and `pmc6130389_supp.zip`.
- **Full-text-extracted and searched the actual PDF** (not a summary, not a guess): its only table (Table S1) is spectral absorption-band wavelength characteristics (1.0–2.5 µm band centers/shoulders), **not a coordinate list**. The ice detections themselves are presented **only as a figure** (SI Appendix Fig. S5: "Ice exposures overlain on the Diviner annual maximum bolometric temperature... cold traps not showing ice exposures at craters Bosch... Hedervari, Amundson, Idel'son L, and Wiechert are circled in blue") — an image/map, exactly the case the task instructed to flag as insufficient.
- No PDS Geosciences Node, USGS, or other archive listing of the M3-derived ice-detection pixel coordinates was located.

**What WAS found and is usable, per the task's fallback allowance for "published coordinate table" and "other authoritative datasets":**
1. **LCROSS Cabeus impact coordinate** — a genuine, precise, published point coordinate: Marshall et al. (2011), *Space Science Reviews*, doi:10.1007/s11214-011-9765-0 — Centaur impact at **−84.6796°, −48.7093°** (311.2907°E), 1σ uncertainty 115 m (lat) / 44 m (lon).
2. **Named craters** from Li et al. 2018's own text and SI Fig. S5 — 7 positive (Faustini, de Gerlache, Haworth, Shoemaker, Sverdrup, Shackleton, Rozhdestvenskiy) and 5 explicitly-negative (Amundsen, Hedervari, Idel'son L, Wiechert, Bosch). Crater **center coordinates and diameters** obtained from the **USGS Gazetteer of Planetary Nomenclature** (the official IAU-approved database), reproduced via each crater's Wikipedia infobox (the Gazetteer's own search endpoint returned server errors this session; Wikipedia infoboxes for these craters cite the Gazetteer directly as their source).

**This is a real, non-fabricated, but *crater-level* reference set — not the pixel-level M3 dataset the task asked for first.** The crater center is a proxy for "ice was detected somewhere within this crater," not the exact M3 pixel location. This limitation is carried through every output below, not hidden.

---

## TASK 2 — Reference site table

13 sites total: 8 positive (7 M3 + LCROSS), 5 control. Full table: `outputs/validation/ice_reference_sites.csv`, `control_sites.csv`.

| Site | Category | Lat | Lon | Region | In PRISM PSR catalog? | Y4R/CPR/SERD/T-Ratio coverage | DFSAR/DOP coverage |
|---|---|---:|---:|---|---|---|---|
| LCROSS Cabeus | positive (HIGH) | −84.680 | −48.709 | south | **True** (SP_844580_3134320) | Yes | Not tested |
| Faustini | positive (MODERATE) | −87.3 | 77.0 | south | **True** (SP_871460_0840750) | Yes | Not tested |
| de Gerlache | positive (MODERATE) | −88.5 | −87.1 | south | False | Yes | Not tested |
| Haworth | positive (MODERATE) | −86.9 | −4.0 | south | **True** (SP_874930_3578760) | Yes | Not tested |
| Shoemaker | positive (MODERATE) | −88.1 | 44.9 | south | **True** (SP_880260_0452790) | Yes | Not tested |
| Sverdrup | positive (MODERATE) | −88.5 | −152.0 | south | **True** (SP_882490_2164550) | Yes | Not tested |
| Shackleton | positive (MODERATE) | −89.67 | 129.78 | south | **True** (SP_896450_1282030) | Yes | Not tested |
| Rozhdestvenskiy | positive (MODERATE) | 85.2 | −155.4 | **north** | N/A | **NO COVERAGE** | **NO COVERAGE** |
| Amundsen | control | −84.5 | 82.8 | south | False | Yes | Not tested |
| Hedervari | control | −81.8 | 84.0 | south | False | Yes | Not tested |
| Idel'son L | control | −84.2 | 115.8 | south | False | Yes | Not tested |
| Wiechert | control | −84.5 | 165.0 | south | False | Yes | Not tested |
| Bosch | control | 86.82 | 133.6 | **north** | N/A | **NO COVERAGE** | **NO COVERAGE** |

**PSR-catalog note:** de Gerlache and all 4 south-pole control craters are **not** matched to any polygon in PRISM's local LOLA PSR shapefile at their centroid coordinate — this is expected (crater centroids frequently fall outside the specific small permanently-shadowed sub-polygon, which is usually offset toward the crater floor) and is reported as-found, not adjusted.

**North-pole sites (Rozhdestvenskiy, Bosch): NO COVERAGE, stated honestly.** PRISM's Y4R/CPR/SERD/T-Ratio mosaics and LOLA PSR catalog are south-polar-only products. These 2 sites could not be evaluated and are excluded from all statistics below — they are not silently dropped; their `NO_COVERAGE` status is recorded in both CSVs.

**DFSAR/DOP coverage: NOT TESTED for any of the 13 sites.** Establishing DOP coverage requires the same acquisition-hunt-and-download workflow used for the original candidate (true-image-footprint-corner screening of the 602-manifest + Grid CSV confirmation, then downloading a 1–2 GB product) — not attempted for 13 additional sites in this task, per its explicit scope. This is stated as a real gap, not implied to be complete.

---

## TASK 3 — Reference area

`outputs/validation/ice_reference_area.geojson` (13 features, 1 GeoJSON per site).

**Important distinction, not glossed over:** the polygons in this GeoJSON are **crater-disk approximations** (a small-circle of the crater's own radius around its USGS-Gazetteer center coordinate) — **not** the true M3 ice-detection pixel footprint, which (per Task 1) is not published in machine-readable form anywhere located this session. "Reference area" below means "the crater used as the sampling region," not "area confirmed to be ice."

| Site | Diameter (km) | Crater-disk area (km²) |
|---|---:|---:|
| LCROSS Cabeus | — (point measurement) | — |
| Faustini | 39.0 | 1,194.6 |
| de Gerlache | 32.4 | 824.5 |
| Haworth | 51.4 | 2,075.0 |
| Shoemaker | 50.9 | 2,034.8 |
| Sverdrup | 35.0 | 962.1 |
| Shackleton | 21.0 | 346.4 |
| Rozhdestvenskiy | 177.0 | 24,605.7 (north, no PRISM data) |
| Amundsen | 103.4 | 8,395.5 |
| Hedervari | 69.0 | 3,739.3 |
| Idel'son L | 28.0 | 615.8 |
| Wiechert | 41.0 | 1,320.3 |
| Bosch | 19.6 | 301.1 (north, no PRISM data) |

No area was estimated from a screenshot; all figures come from official crater diameters (USGS Gazetteer) via simple disk geometry, stated as an approximation.

---

## TASK 4 — Positive / control set

Constructed exactly as defined at the top of this document. **No PSR was labeled "ice-positive" merely because it is permanently shadowed** — every positive site has independent evidence cited in §1/Task 2; every control site has an explicit negative finding cited from Li et al. 2018, not silence.

---

## TASK 5 — PRISM pipeline run on reference sites

Code: `src/validation_sites.py` (site table), `src/validation_pipeline.py` (extraction — reuses `read_window`/CRS-transform logic identical in method to `src/candidate_physics_pipeline.py`, no formula changes), `src/build_validation_outputs.py` (aggregation). Window size scaled to each crater's own radius (LCROSS: fixed 1 km half-window, reflecting its point-measurement scale, not a crater).

### Pv / CPR / SERD / T-Ratio distributions (11 south-pole sites tested: 7 positive, 4 control)

| Metric | Positive mean (n=7) | Positive median | Control mean (n=4) | Control median |
|---|---:|---:|---:|---:|
| Pv | 0.2715 | 0.2505 | 0.2862 | 0.2865 |
| CPR | 0.2791 | 0.2495 | 0.2808 | 0.2862 |
| SERD | 0.8055 | 0.8219 | 0.7977 | 0.7970 |
| T-Ratio | 0.2990 | 0.2690 | 0.2995 | 0.3061 |

**These distributions are statistically indistinguishable between positive and control groups** — every mean/median pair above differs by far less than either group's own standard deviation. Full percentile tables, pixel counts, and NaN%: `outputs/validation/validation_metrics.json`, `ice_reference_sites.csv`, `control_sites.csv`.

### Physics-evidence-score analog (Pv/CPR/T-Ratio relative-percentile composite, same construction as `src/physics_evidence_score.py`'s normalization method, SERD excluded for the same documented reason)

| Rank | Site | Category | Score | In PSR catalog? |
|---:|---|---|---:|---|
| 1 | Shackleton | positive | 0.920 | True |
| 2 | de Gerlache | positive | 0.719 | False |
| 3 | **Wiechert** | **control** | 0.714 | False |
| 4 | **Amundsen** | **control** | 0.688 | False |
| 5 | Faustini | positive | 0.662 | True |
| 6 | **Idel'son L** | **control** | 0.612 | False |
| 7 | Sverdrup | positive | 0.540 | True |
| 8 | **Hedervari** | **control** | 0.530 | False |
| 9 | Haworth | positive | 0.477 | True |
| 10 | Shoemaker | positive | 0.370 | True |
| 11 | **LCROSS Cabeus** | **positive (HIGH confidence)** | **0.320** | True |

Full ranking table: `outputs/validation/validation_metrics.json` → `pooled_ranking_by_evidence_score`.

### Systematic-separation check

```
positive_mean_score:   0.573
control_mean_score:    0.636
positive_median_score: 0.540
control_median_score:  0.650
n_positive_above_control_median: 3 of 7
```

**Verdict (as computed, not adjusted): "Positive sites do NOT score higher on average than control sites in this sample — this does NOT support the hypothesis that PRISM's radar evidence score systematically separates independently-identified ice sites from checked-negative controls."**

### Terrain

Slope (LOLA `LDSM`, real windowed remote read, same method as `src/terrain_pipeline.py`) mean per site is included in `ice_reference_sites.csv`/`control_sites.csv` (`slope_deg_mean`). No systematic pattern was tested for beyond inclusion in the raw table — not a focus of this task's headline comparison.

### DOP

**Not computed for any reference site.** See Task 2 note above.

---

## Visualization

`outputs/validation/validation_comparison.png` — side-by-side box plots (ICE-REFERENCE vs CONTROL) for Pv, CPR, SERD, T-Ratio, and the evidence-score analog, individual sites overplotted as points.

---

## Interpretation — read carefully, do not over-interpret in either direction

1. **This is a small sample** (7 positive, 4 control, south-pole only) built on **crater-level**, not pixel-level, ground truth. A null result here does not definitively refute PRISM's screening approach, and a positive result would not have definitively confirmed it either — the sample is too small and the reference resolution too coarse for a strong statistical claim in either direction.
2. **The null result is nonetheless a real, unfavorable finding that should not be minimized.** PRISM's Pv/CPR/T-Ratio-based evidence score, as currently constructed (relative-percentile-in-mosaic composite, unweighted), does not cleanly separate this validation set's positive and control craters. The fact that LCROSS Cabeus — the one site with a direct physical measurement rather than a remote spectral inference — scores lowest of all 11 tested sites is a specific, notable, and unflattering data point that should inform how much confidence is placed in PRISM's current radar-only screening.
3. **Possible (untested) explanations, listed without asserting any of them:** crater-centroid coordinates may not land on the actual ice-bearing sub-region within large craters (a known limitation, §Task 1); the M3 criterion itself is independently disputed in the literature (a Research Square preprint argues Sinha et al.'s related CPR formula is "incorrect" and that CPR/DOP variation is "fully consistent with different levels of near-surface roughness," not a definitive ice indicator — see the DOP audit in this session's prior turn); PRISM's Pv/CPR/T-Ratio window statistics may be dominated by factors uncorrelated with M3-detected surface ice (radar volume scattering and 3 µm surface-ice spectral absorption are physically different phenomena probing different depths and mechanisms, and were never guaranteed to agree).
4. **No PRISM output, threshold, weighting, or the candidate pipeline was modified as a result of this validation**, per explicit instruction.

## Files created

- `outputs/validation/ice_reference_sites.csv`
- `outputs/validation/control_sites.csv`
- `outputs/validation/ice_reference_area.geojson`
- `outputs/validation/validation_metrics.json`
- `outputs/validation/validation_comparison.png`
- `outputs/validation/validation_raw_results.json` (full per-site raw stats)
- `outputs/validation/refs/pnas.1802345115.sapp.pdf`, `pmc6130389_supp.zip` (downloaded source SI material, kept for traceability)
- `src/validation_sites.py`, `src/validation_pipeline.py`, `src/build_validation_outputs.py`
