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

## YOLOv8 — still not implemented, but the OHRC blocker is resolved (real optical coverage now exists)

`src/cnn_yolo_interface.py` exists, but it's a **typed interface stub**, not a model: `Yolov8BoulderDetector.detect()` raises `NotImplementedError` with an explanation rather than returning a fabricated result. Calling `integration_status()` returns `"PLANNED / NOT TRAINED"` for both YOLOv8 and a CNN alternative. Originally two blockers; one is now resolved:

1. **No labeled training data exists anywhere in this project.** Zero occurrences of boulder/hazard/ice bounding-box or segmentation labels — confirmed by the original audit (`PROJECT_STATUS.md` §4) and re-confirmed this session. **Still true, still blocking.**
2. ~~No OHRC optical scene covering the candidate exists yet.~~ **Resolved 2026-08-23 — but by abandoning OHRC, not by finding an OHRC scene.** See below.

### OHRC is a dead end; NASA LROC NAC replaces it — real coverage found and downloaded

CH2Browse (ISSDC's map-based footprint browser, the fix this doc previously recommended) was tried by the user directly: a 4°×4° box around the candidate returned **"0 to 0 of 0 entries."** Confirmed empirically — Chandrayaan-2 OHRC has essentially no south-polar coverage this close to the candidate. Not a search-technique failure; the data isn't there.

The actual need was never "OHRC specifically," it was *any* real optical imagery covering the candidate. **NASA's LROC NAC archive (`data.lroc.im-ldi.com`) — a different mission (LRO, not Chandrayaan-2), public, no login — does have coverage**, found via its real coordinate-search form and confirmed with a proper point-in-polygon containment test (not a loose bounding box — see the false-positive/correction story in `CANDIDATE_ACQUISITION_SELECTION.md` Addendum 4, the same class of mistake Addendum 2 already documents for DFSAR). Downloaded and pixel-verified:

| Candidate | Frame | Resolution | Size | Valid px |
|---|---|---:|---:|---:|
| `SP_842420_0421060` | `M1500885449LC` (CDR) | 0.93 m/px | 528.9 MB | 99.3% |
| `SP_840980_0797630` (primary) | `M1524271502RC` (CDR) | 2.14 m/px | 264.5 MB | 98.7% |

Both from NASA's official PDS mirror, no credentials. Saved under `data/raw/lroc_nac/`. These are CDR (radiometrically calibrated) products, **not map-projected** — `PRISM/src/lroc_nac_georeference.py` builds an approximate GCP-based affine (4 corner lat/lons → `rasterio.transform.from_gcps`, ~30 m residual) to locate and crop the candidate's neighborhood; this is explicitly `DERIVED / APPROXIMATE` geolocation, not full SPICE/ISIS photogrammetry. Full method, the mosaic-vs-per-frame tradeoff, and the exact form-submission fixes needed to make the search tool work are in `CANDIDATE_ACQUISITION_SELECTION.md` Addendum 4.

**Correction, caught by direct user review of the preview image:** the primary candidate's NAC crop isn't just dim, it's noise-floor — adjacent-pixel spatial correlation −0.077 (real terrain typically shows 0.7–0.95+), meaning the "dim" framing above undersold a real problem: this specific crop carries no usable surface signal, full stop. This is a genuine physical limitation, not a bug — the PSR interior gets zero direct sunlight, and a conventional camera like NAC (or OHRC) only has scattered light to work with, below its noise floor here. **NASA ShadowCam — a camera ~200x more sensitive than NAC, purpose-built for imaging PSR interiors — fixes this for the primary candidate**: a real, properly map-projected, coordinate-searchable archive (`data.im-ldi.com`, dataset `luna_shadowcam_pds`), 25 true-polygon-verified frames found covering the candidate, best one (`M015379790SE`, 82.0° incidence, 1.69 m/px) windowed-read directly from its Cloud-Optimized GeoTIFF (no full download needed) and verified with **0.994 adjacent-pixel correlation — genuine terrain signal**. Full method and false-positive story: `CANDIDATE_ACQUISITION_SELECTION.md` Addendum 5. The shortlisted candidate's NAC crop, by contrast, was checked the same way and does hold real signal (0.423 correlation) — no replacement needed there, though ShadowCam coverage exists for it too (23 verified frames) if wanted later.

### The labeling blocker is resolved too — a real, published, YOLOv8-ready boulder dataset exists

Found and downloaded (2026-08-23, same day as the ShadowCam correction above): **BoulderNet / YOLOv8-BeyondEarth** (Prieur et al. 2023, *JGR Planets*, ASU/Marie Skłodowska-Curie BOULDERING project). This isn't a paper describing a method — it's the actual labeled dataset, already in YOLOv8 instance-segmentation format:

- **Source:** `zenodo.org/records/14250874`, `bouldering_dataset_2024_YOLO_and_detectron2_format.zip`, 601.4 MB, no login. Downloaded to `data/raw/boulder_net/` (gitignored, same convention as other raw data). Byte count verified exact match (601,409,488 bytes), 9,972 files extracted cleanly.
- **Composition, checked directly (not taken from the paper's abstract):** train split 3,958 images, **3,703 of them (93.6%) are real LROC NAC lunar images** (filenames match the same `M<digits><LE/RE>` convention as this project's own NAC downloads) — not a Mars/Earth-analog dataset with a token lunar subset. Remainder is Mars HiRISE (`ESP_...`) and terrestrial drone imagery (Sierra Nevada boulder fields) from the same fieldwork project.
- **Format:** standard YOLOv8 polygon-segmentation `.txt` labels (one file per image, normalized polygon vertices), single class `boulder`, `yolo_inst_seg_boulder_dataset.yaml` config (paths were Windows-local to the original author — a corrected local version was written: `data/raw/boulder_net/boulder2024/yolo_inst_seg_boulder_dataset_local.yaml`).
- **Verified real, not just present:** rendered the actual polygon labels over an actual training image (`M104827900_0175_image.png`, 17 real boulder annotations) and visually confirmed the polygons trace real boulders in the image, not placeholder/corrupt data. Saved: `PRISM/outputs/objective_optical/boulder_net_sample_annotated.png`.
- **Honest correction to an earlier claim:** a companion Zenodo record (`14579518`) was initially reported as containing trained model weights. Checked directly — it's the `YOLOv8-BeyondEarth` **code repository only** (training/prediction/dataset-conversion scripts, no `.pt` weights file). A third record (`14253940`, 27.4 GB) contains the *output* of their trained model (2M+ detected boulders around 82 lunar/Mars craters) but not the weights either, and wasn't downloaded (too large, not needed — we have the labels to train our own). **There is no shortcut to a ready-to-run pretrained model; training is still required**, but the "no labeled data anywhere" blocker that made training impossible is now fully resolved.
- **Local training is feasible:** this machine has PyTorch 2.13 with Apple MPS (Metal GPU) available — checked directly, not assumed. `ultralytics` (the YOLOv8 package) is not yet installed.

### BoulderNet dropped entirely — user decision, 2026-08-23

BoulderNet (Prieur et al. 2023) was downloaded, verified real, found to contain ~5% genuine Earth drone imagery, filtered down to a lunar+Mars-only copy — and then the user reviewed it and rejected it outright ("the bouldernet doesnt seem right to me, please get rid of that completely"). Removed completely: `data/raw/boulder_net/` (original 601MB zip, extracted files, and the filtered `boulder2024_lunar_only/` copy, ~1.8GB total) and the label-verification image (`boulder_net_sample_annotated.png`). Nothing from it was ever committed to git (it lived under gitignored `data/raw/`).

**Net effect: the "no labeled boulder/hazard training data" blocker is back to blocked.** No supervised YOLOv8/CNN boulder detector can be trained until either (a) a different labeled dataset is found and the team is satisfied with its provenance, or (b) manual/semi-automated annotation is done directly on the real ShadowCam/NAC crops this project already has, or (c) the project falls back to a classical/unsupervised approach (blob detection, shadow/brightness-based boulder proxies) instead of a trained detector.

### BoulderNet re-acquired, this time strictly lunar-only (2026-08-23, later same day)

After the terrain-visualization work below, the user confirmed they want to proceed with a labeled dataset after all (option 1 from the earlier discussion), with one hard constraint: "strictly stick with non-earth data... I want the model to be as accurate as possible on the test set." Re-downloaded BoulderNet from Zenodo (byte-exact match again, 601,409,488 bytes; the first attempt this time dropped mid-transfer at ~5MB and was resumed with `curl -C -`). Filtered **stricter than the first pass**: this time both Earth (Sierra Nevada drone sites) *and* Mars (HiRISE) images are excluded, keeping only real LROC NAC lunar imagery, across all three splits so the held-out test set is clean too:

| Split | Original | Kept (lunar-only) | Dropped |
|---|---:|---:|---:|
| train | 3,957 | 3,719 | 238 |
| validation | 739 | 697 | 42 |
| test | 280 | 262 | 18 |

Mars is technically "non-Earth" and was kept in an earlier same-day pass, but dropped this time as the more conservative choice given the explicit "as accurate as possible on the test set" instruction for a lunar-specific task — documented in `data/raw/boulder_net_clean/README.md`, including how to add Mars back (a quick re-filter, not a re-download) if more training volume is wanted later. The raw unfiltered zip and extracted original were deleted immediately after filtering this time (not kept alongside the clean copy). Spot-verified with a random real sample (`M110797848_00035`, 2 real boulder annotations rendered over the real image) — sent to the user directly. Location: `data/raw/boulder_net_clean/` (gitignored), config `yolo_boulder_lunar_only.yaml`. Training itself still not yet run.

### Priority shift, same day: real 3D terrain reconstruction, not (yet) boulder detection

User's direction: use the confirmed-real ShadowCam imagery (see below) together with the existing real LOLA DEM data to build **actual 3D terrain models of the candidate regions**, so the frontend's maps/animations render real Moon surface geometry instead of synthetic placeholders. This is now the priority; automated boulder/hazard detection (YOLOv8 or otherwise) is deprioritized until a labeling approach is decided. See `DECISIONS.md` for the concrete plan.

### NAC artifacts removed — fully superseded by ShadowCam

Once ShadowCam was confirmed real and available for all 7 shortlisted candidates (below), the NAC crops became redundant: the primary candidate's NAC crop was confirmed noise anyway, and the shortlisted candidate's real-but-lower-quality NAC crop (0.423 correlation vs. ShadowCam's 0.996-0.997) added no value. Removed per user request: both NAC crop TIFFs/JSONs/previews, `PRISM/src/lroc_nac_georeference.py` (the approximate-GCP-projection script, unused now that ShadowCam ships already-map-projected COGs), and the raw `data/raw/lroc_nac/` downloads (~800MB). The written record of what was tried and why (the false-positive story, the DEFLATE-compressed-mosaic dead end) stays in Addenda 4-5 above — only the now-redundant binary files are gone.

### ShadowCam coverage extended to the full 7-candidate shortlist, visually verified — confirmed usable by the user

Per user request (visually verify, not just trust stats): `PRISM/src/shadowcam_batch_verify.py` reruns the same real-coverage method (true polygon containment on decoded WKB footprints, quality-flag filtering, windowed COG reads) across the 6 remaining shortlisted candidates, 2 best (lowest-incidence) frames each. **All 12 verified real** — every single one passed the adjacent-pixel-correlation check that caught the earlier NAC noise problem:

| Candidate | Frames checked | Adjacent-pixel correlation range |
|---|---:|---:|
| `SP_832640_0090770` | 2/21 available | 0.995 – 0.996 |
| `SP_830080_0535120` | 2/20 available | 0.982 – 0.988 |
| `SP_842420_0421060` | 2/23 available | 0.996 – 0.997 |
| `SP_817950_1586580` | 2/17 available | 0.971 – 0.996 |
| `SP_819860_1568660` | 2/17 available | 0.989 – 0.993 |
| `SP_809570_2454450` | 2/4 available | 0.988 – 0.991 |

Every shortlisted candidate has at least 4 real, quality-flagged ShadowCam frames available (up to 23 for `SP_842420_0421060`); only the best 2 per candidate were downloaded/verified. Crops + preview PNGs: `PRISM/outputs/objective_optical/shortlist_shadowcam/`, full stats in that directory's `summary.json`. All previews sent directly to the user for visual review.

### What's still needed before YOLOv8 is real
Training itself hasn't been run yet. Next step: `pip install ultralytics`, fine-tune on the filtered lunar(+Mars) dataset (optionally combined with the real optical crops acquired this session — ShadowCam for the primary candidate, NAC for the shortlisted one — as inference/validation targets, not training data, since neither has boulder labels of its own).

## What this means for the frontend
Ice Detection (Module 1) can honestly say: real Isolation Forest, three runs, growing coverage (primary → full shortlist this session), per-pixel version genuinely independent. Surface Hazards / boulder detection (Module 2's optical half) can now say "real optical imagery acquired (LROC NAC, not OHRC), boulder detection not yet built" — an upgrade from "OHRC pending," but still short of an actual detector until labeling or a classical fallback is built.
