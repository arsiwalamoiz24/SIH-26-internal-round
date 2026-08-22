# ML Methods — Isolation Forest (done) and YOLOv8 (not done)

**Date:** 2026-08-23. Answers the question "did we implement the Isolation Forest for ice detection and YOLOv8 for hazard mapping we planned?" — yes and no, respectively, and this explains both.

## Isolation Forest — implemented, three runs, two genuinely different in kind

`sklearn.ensemble.IsolationForest`, unsupervised anomaly detection — used because there are no ground-truth ice labels anywhere in this project to train a supervised classifier against (see `REFERENCE_PROJECT_COMPARISON.md` for why that's a deliberate choice, not a gap).

### v1 — PSR-level, all 336 radar-covered PSRs (`src/ml_anomaly_pipeline.py`)
- **Sample = one PSR.** 336 rows, features = `area_km2, px_with_radar_data, high_tier_fraction, moderate_plus_fraction`.
- **Circularity caveat (real, not a formality):** all 4 features are *derived from* the same Y4R Pv computation that already produced the candidate's shortlist ranking (`src/radar_pipeline.py`). An anomaly finding here cannot be claimed to *independently validate* the Pv-based selection — the script's own docstring says so. It exists to satisfy "implement an ML pipeline" with a real, adequately-sized sample, not as independent confirmation.
- Primary candidate result: anomaly rank **40 of 336**.
- Output: `outputs/objective1/ml/isolation_forest_results.json`, `anomaly_scores_all_psrs.csv`.

### v2 — per-pixel, primary candidate only (`src/ml_pixel_anomaly_pipeline.py`)
- **Sample = one pixel** inside the candidate's 264×264px (25m/px) window. Features = **Pv, CPR, SERD, T-Ratio measured at that pixel** — four independently-measured radar quantities, not aggregates derived from each other. No circularity caveat applies.
- This is the version that actually matches the original plan (PROJECT_GUIDE.md): an Isolation Forest producing a spatial "ice probability map," not a per-PSR bar chart. It backs the `evidenceGrid.probIceGrid` the frontend's Ice Detection page renders (previously synthetic placeholder data — see `DECISIONS.md`).
- Data access: the real Y4R (evn/vol/odd/hlx) and L3C (cpr/srd/trt) GeoTIFF bands, read via GDAL `/vsicurl/` windowed remote reads against the team's shared-Drive-hosted files — no multi-GB download. Verified byte-accurate against `PHYSICS_RESULTS.json`'s official Track A stats before trusting it.
- Result: PSR interior mean ice-likelihood **0.194** vs. **0.177** outside — real, but a modest separation, reported honestly rather than oversold.
- Output: `outputs/objective1/ml/pixel_anomaly_map.json`, `pixel_anomaly_grids.npz`.

### v2, extended — the other 6 shortlisted PSRs (`src/ml_pixel_anomaly_shortlist_pipeline.py`)
Same per-pixel, independent-feature method as v2, run for the remaining 6 PSRs in Objective 1's 7-candidate shortlist (previously only the primary candidate had this). Same data-access technique (cached, still-valid `/vsicurl/` URLs in `data/raw/candidate_window_urls.json`). Output: `outputs/objective1/ml/shortlist/*_pixel_anomaly.json` + `shortlist_pixel_anomaly_summary.csv` comparing PSR-interior-vs-outside ice-likelihood separation across all 7.

**Real result, reported as found:** 5 of 7 shortlisted PSRs show positive interior-vs-outside separation (interior pixels score more anomalous), 2 show slightly negative separation. `SP_819860_1568660` shows the *largest* separation (0.097) — notably stronger than the primary candidate's own 0.017. This doesn't change the primary candidate's status (it's still #1 by the Physics Evidence Score, a different and more heavily-weighted metric — see `PHYSICS_RESULTS.md`), but it's a real data point worth someone's attention rather than filing away quietly: an independent per-pixel method finding a *stronger* anomaly signal at a lower-ranked shortlist candidate is exactly the kind of thing a second evidence source is supposed to surface.

| PSR_ID | interior | outside | separation |
|---|---:|---:|---:|
| SP_819860_1568660 | 0.280 | 0.183 | **+0.097** |
| SP_809570_2454450 | 0.217 | 0.156 | +0.061 |
| SP_840980_0797630 (primary) | 0.194 | 0.177 | +0.017 |
| SP_830080_0535120 | 0.210 | 0.197 | +0.012 |
| SP_832640_0090770 | 0.183 | 0.174 | +0.009 |
| SP_842420_0421060 | 0.189 | 0.196 | −0.007 |
| SP_817950_1586580 | 0.173 | 0.187 | −0.015 |

**Scope decision — no regional pixel-level pass.** Unlike the hazard-mapping work (which added a genuine regional overview tier — see `DECISIONS.md`), this stays at per-candidate window scale. Objective 1's own radar screening already covers the *entire* south-polar region at PSR-aggregate scale (that's what produced the 336-PSR candidate table and Isolation Forest v1 above). A regional *pixel*-level pass would require the full Y4R/L3C mosaics at native resolution — the exact multi-GB-download problem the windowed-read technique exists to avoid, for marginal benefit over what v1 already provides at regional scale.

## YOLOv8 — not implemented, and here's exactly why

`src/cnn_yolo_interface.py` exists, but it's a **typed interface stub**, not a model: `Yolov8BoulderDetector.detect()` raises `NotImplementedError` with an explanation rather than returning a fabricated result. Calling `integration_status()` returns `"PLANNED / NOT TRAINED"` for both YOLOv8 and a CNN alternative. Two real, checked blockers, not excuses:

1. **No labeled training data exists anywhere in this project.** Zero occurrences of boulder/hazard/ice bounding-box or segmentation labels — confirmed by the original audit (`PROJECT_STATUS.md` §4) and re-confirmed this session.
2. **No OHRC optical scene covering the candidate exists yet.** The one OHRC scene physically present (`ch2_ohr_ncp_20251010T0942085687_d_img_d18`) was independently confirmed to be a narrow strip within ~24km of the pole — the candidate `SP_840980_0797630` is ~179km from the pole. Training or running inference "for the candidate" on this scene would describe the wrong patch of the Moon.

### Where to actually find OHRC data covering the candidate
PRADAN's product-search interface is hard to use for this specific problem because it makes you search by product ID/date rather than by location — you need to already know which product covers your coordinates, which is exactly what's unknown here. The fix:

- **CH2Browse — `https://chmapbrowse.issdc.gov.in`** — ISSDC's *map-based* footprint browser for Chandrayaan-2, separate from PRADAN's form search. Lets you visually locate footprints over a target lat/lon (−84.098°, 79.764°) and pick the OHRC product that actually covers it, instead of guessing product IDs. This is the recommended next step for closing the OHRC blocker.
- Published research confirms OHRC-of-PSR data exists and is usable at this resolution (e.g. a Cabeus-crater PSR OHRC study identified boulders/craters as small as 1.5–1.8m at <0.3m/px) — this is a data-*discovery* problem, not a data-*availability* problem. See `CANDIDATE_ACQUISITION_SELECTION.md` for the same lesson learned the hard way with the DFSAR raw product (loose bounding-box corners giving false-positive coverage matches — the same trap likely applies to OHRC footprint search, so confirm with the product's true rotated footprint corners or a map tool like CH2Browse, not an axis-aligned bounding box).
- Once a covering scene is found: **no labels still means no YOLOv8/CNN training.** The next real step after acquiring the scene would be manual/semi-automated boulder annotation on that one scene (there's no shortcut around needing *some* labeled data for a supervised detector), or falling back to an unsupervised/classical approach (e.g. blob detection + morphology, or brightness/shadow-based boulder proxies) if time doesn't allow labeling — that would be a different, simpler method than YOLOv8, and should be labeled as such if built, not presented as "YOLOv8."

## What this means for the frontend
Ice Detection (Module 1) can honestly say: real Isolation Forest, three runs, growing coverage (primary → full shortlist this session), per-pixel version genuinely independent. Surface Hazards / boulder detection (Module 2's optical half) should keep saying "OHRC pending" — that's still accurate, not stale — until a covering scene is actually acquired via CH2Browse.
