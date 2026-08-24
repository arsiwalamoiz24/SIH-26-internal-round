# PRISM — Decision Log

This file explains **what we're building, why, and the decisions made along the way** — so anyone on the team can catch up without re-deriving context. It's a living document: add to it, don't just overwrite it. For the full plain-English project explainer see `PROJECT_GUIDE.md`; this file is specifically about *decisions and their reasoning*.

---

## What PRISM is

PRISM screens Chandrayaan-2 DFSAR radar data for water-ice signatures inside the Moon's permanently shadowed south-polar craters (PSRs), cross-checks candidates against real terrain hazard (slope/roughness/illumination), and plans a landing site + rover route to reach the best one. Four linked questions, one pipeline:

1. Where is the ice? (radar screening — **Module 1**)
2. Where's safe to land nearby? (terrain hazard — **Module 2**)
3. Where's the best landing site? (Objective 3)
4. What's the safest rover path in? (Objective 4)

The primary candidate the whole pipeline is built around: **PSR `SP_840980_0797630`**, −84.098°, 79.764°, area 14.234 km².

**Naming note:** this project is called **PRISM** everywhere. An early planning doc used "NIDHI" — that name is stale, don't use it anywhere new.

---

## Module ownership (from PROJECT_GUIDE.md's team breakdown)

| Module | Owns | Status as of 2026-08-22 |
|---|---|---|
| 1 — Ice Detection & Backend | Radar screening (Pv/CPR/SERD/T-Ratio), Isolation Forest, FastAPI-equivalent data layer | Real pipeline output exists and is wired into the frontend |
| 2 — Hazard Mapping (terrain) | LOLA DEM slope/roughness/illumination/combined hazard | Primary candidate done; regional + shortlist in progress (this session) |
| 2b — Hazard Mapping (optical) | OHRC imagery, boulder detection (YOLOv8/CNN) | Not started — no OHRC scene covering the candidate has been confirmed yet |
| 3 — Landing Site Selection | Slope + solar + ice-proximity scoring | Derived/illustrative model, not yet fed by real Module 2 hazard scores |
| 4 — Rover Traverse | A* pathfinding over a hazard-weighted cost grid | Illustrative model, not yet fed by real hazard data |
| 5/6 — Frontend (2D + 3D) | Dashboard, map layers, terrain visualizer | Built; data-wiring is ongoing (this log tracks what's real vs. illustrative) |

---

## Decisions made, and why

### The repo was a mess — restructured it
**What:** Moved multi-GB raw data (`CPR.tif`, `DOP.tif`, raw acquisition folders) into a gitignored `data/raw/`, removed vendored clone repos (`worldstrat/`, `scratch/repos/*`) that had nothing to do with PRISM, sorted loose root scripts into `scripts/legacy/` (utility, tracked) vs `scripts/local_only/` (contains hardcoded API credentials — gitignored, **rotate those credentials if this repo is ever made public**).
**Why:** New teammates/judges opening the repo should see the actual project, not a graveyard of one-off scripts and abandoned experiments.

### Module 1's frontend data was stale — reconnected it to the real pipeline
**What:** `prism_science_data.json` (the frontend's data source) had numbers from an earlier notebook run. A same-day teammate session had already produced a more rigorous, more complete result set (`PRISM/outputs/objective1/PHYSICS_RESULTS.json` — Physics Evidence Score, DOP, candidate-specific stats) that was sitting unused.
**Why:** Shipping a dashboard with stale numbers next to a repo that has newer, better numbers is worse than not having a dashboard.

### Isolation Forest: kept the honest weak version, added a genuinely strong one
**What:** The existing Isolation Forest (`ml_anomaly_pipeline.py`) scores 336 PSRs as *samples* using features derived from the same Pv computation that already ranked them — its own docstring correctly flags this as circular, not independent evidence. Rather than replace it, we added `ml_pixel_anomaly_pipeline.py`: a **second, independent** Isolation Forest where each *pixel* in the candidate's window is a sample, and its 4 features are real, separately-measured radar bands (Pv, CPR, SERD, T-Ratio) — no circularity.
**Why:** The circular version is still a legitimate answer to "did you implement an ML pipeline" for the pitch; the pixel version is the one that actually matches the original plan's "ice probability map" concept, and now backs the frontend's probability-surface visualization with real data instead of a synthetic placeholder grid.
**How we got the data without a multi-GB download:** the team's shared Google Drive had the individual (unzipped) Y4R/L3C GeoTIFFs with public, range-request-capable direct-download links. Used GDAL's `/vsicurl/` to read only the ~264×264px candidate window remotely — same trick as the terrain pipeline already used for the LOLA DEM. Verified byte-accurate against the known-correct Track A stats before trusting it.

### Hazard mapping had a real bug — found it before it shipped
**What:** A teammate's notebook (`obj2_probably.ipynb`) meant to compute slope/roughness/illumination from elevation, but its DEM-loading cell actually read `LDSM_80S_20MPP_ADJ.TIF` (NASA's *pre-computed slope* raster) instead of `LDEM_80S_20MPP_ADJ.TIF` (elevation). Caught because the notebook's printed "elevation range" (0.007–59.3) was an exact match to this project's own prior *slope* statistics. Fixed in `hazard_map_pipeline.py`, which reads the correct raster.
**Why this matters:** every downstream number in the original notebook (slope-of-slope, roughness of slope values, shadow-casting against slope-as-height) was computed on the wrong physical quantity. The fixed version cross-validates cleanly: its own Sobel-gradient slope agrees with NASA's independently-precomputed slope to within 0.01° mean, and the PSR interior shows exactly 0.0 illumination across 24 simulated sun positions — an independent geometric confirmation it's genuinely permanently shadowed, not just an assumption carried from the catalog.

### Dark lunar theme — one file drives the whole site
**What:** Requested a dark, cohesive, non-"vibe-coded" visual theme site-wide, no gradients, no clashing button colors. Rather than hand-editing every page, swapped the ~40 semantic color-token *values* in `globals.css` (the file every page already reads `bg-primary`/`text-on-surface`/etc. from). Had to first fix a few pages (`landing-site`, `rover-traverse`, parts of `simulation`) that had hardcoded hex colors instead of using those tokens — those wouldn't have followed the swap at all.
**Why one file:** any future theme tweak (or reverting to light mode) is now a one-file change, not a per-page hunt. Verified with real screenshots (headless Chromium), not just "the build passed."

### Regional hazard mapping scope: overview resolution, not full native-res
**What:** Timed the illumination ray-casting (`scipy.ndimage.rotate`, run 24× per window) at increasing sizes: 500px→2.2s, 1000px→8.3s, 1500px→19s, scaling close to O(n²). Extrapolated: the full native LOLA grid (30400×30400px, the entire south-polar cap) would take **2+ hours**, need multiple ~3.7GB arrays in memory, and require fetching most of the remote file anyway — defeating the whole point of windowed remote reads.
**Decision:** map a genuinely large region (the same south-polar extent the PSR catalog and Module 1's radar screening already cover — all 653 catalogued PSRs) at an **overview resolution**, the same "screen wide, then go full-res on the shortlist" pattern Module 1's own radar screening already uses (1500px overview → full-res for the 7-candidate shortlist). Full native-resolution mapping of the entire pole isn't planned — most of that area is nowhere near a PSR, and the cost/value tradeoff doesn't justify it.

---

## Regional hazard mapping — done, here's what it found

Ran both tiers described above:
- **Regional overview** (`PRISM/src/hazard_map_regional_pipeline.py`): 1500×1500px overview (405 m/px, 20x decimation) across the *entire* south-polar LOLA extent, all 336 radar-covered PSRs. Real GDAL read timed at 27.7s, full run (read + slope + roughness + 24-pass illumination + hazard + per-PSR aggregation) completed in **34.8 seconds**. Output: `PRISM/outputs/objective2/regional_hazard_overview.json` + `regional_hazard_per_psr.csv` + composite figure showing hundreds of individually-resolved craters.
- **Shortlist full-res** (`PRISM/src/hazard_map_shortlist_pipeline.py`): native 20m/px hazard maps for the other 6 of Objective 1's 7-candidate shortlist (primary candidate was already done). One JSON+PNG per candidate in `PRISM/outputs/objective2/shortlist/`.

**Notable finding, reported honestly rather than cherry-picked:** every one of the 7 shortlisted PSRs shows *exactly* 0.0 mean illumination inside its interior across all 24 simulated sun positions — an independent geometric confirmation that all 7 are genuinely permanently shadowed, not just catalog assumptions. Also: the primary candidate (`SP_840980_0797630`, the #1 ice-evidence-ranked PSR) turns out to have the *lowest* interior hazard score (0.597) of the whole shortlist (others range 0.617–0.792) — best ice evidence and comparatively safest terrain happen to coincide here. That's not guaranteed in general and shouldn't be assumed for future candidates without checking.

Shared algorithm code lives in `PRISM/src/terrain_algorithms.py` (imported by both the single-candidate, shortlist, and regional scripts — one implementation, not three copies).

## Module 1 + Module 2 frontend integration — done

`frontend/src/data/prismDemoData.ts` gained a `REAL_SHORTLIST_CANDIDATES` array (7 entries, all real: Pv/CPR/SERD/T-Ratio from Objective 1's shortlist screening + evidence score/rank from the Physics Evidence Score + slope/hazard/illumination from the new Track G-v2 hazard mapping above). This **replaced** the old map data source (1 real candidate + 25 fabricated `SYNTHETIC_CANDIDATES` points) in `SouthPoleMap.tsx` — the home dashboard map now plots all 7 real shortlisted PSRs, with a toggle between Module 1 (ice-evidence status coloring) and Module 2 (hazard-score coloring) views, and the side panel shows both modules' numbers for whichever candidate is selected.

`candidate/[id]` detail pages gained a third rendering path (`findCandidateById` now returns `kind: "shortlist"` for the 6 non-primary shortlisted PSRs) — before this, clicking any of their map markers led to a real page 404, since only the primary candidate and the fabricated synthetic candidates were previously wired up. The `SYNTHETIC_CANDIDATES` data/rendering path itself was left in place (still used by the comparison/time-series charts, still clearly badged `synthetic_demo`) rather than removed, since replacing those charts' data wasn't in scope here.

## Repo cleanup + ML methods documentation + OHRC sourcing (2026-08-23)

**Constraint this pass worked under:** a teammate was actively editing the frontend live (`git status` showed unstaged changes in `layout.tsx`/`TopNav.tsx` I hadn't made). So cleanup stayed scoped to the repo root and `PRISM/` — nothing moved or renamed inside `frontend/src`.

**What changed:**
- Added this repo's first root `README.md` — one entry point pointing to every doc below.
- Merged `PRISM/doc/` (singular, 1 file) into `PRISM/docs/` (plural, everything else) — the two similarly-named directories were confusing, not meaningfully different in purpose.
- Merged `PRISM/docs/DOP_VALIDATION.md` and `DOP_VALIDATION_RESULTS.md` into one chronological `DOP_VALIDATION.md` (blocked → pipeline validated on a non-candidate acquisition → resolved with the real covering acquisition). The old `DOP_VALIDATION_RESULTS.md` path is kept as a one-line redirect stub rather than deleted, because several real output JSONs (`PHYSICS_RESULTS.json`, `physics_evidence_score.json`, etc.) cite that exact filename in their provenance metadata — breaking that citation would be worse than the redundancy it fixed.
- Deleted `PRISM/outputs/objective2/terrain_analysis_full.png` — a teammate's committed image, generated from the pre-bug-fix version of `obj2_probably.ipynb` (the DEM mixup described above), unreferenced anywhere in code, and very likely showing the wrong hazard map. Recoverable from git history if ever needed.
- Deleted `frontend/src/assets/temp.png` — unreferenced, unused.
- Added a warning docstring to `scripts/extract_notebook_science.py`: it's what originally generated `prism_science_data.json`, but that file has since been extensively hand-edited with real data this script doesn't know about (Physics Evidence Score, DOP, terrain/hazard, the real evidence grid) — re-running it would silently discard all of that.
- New `PRISM/docs/ML_METHODS.md` — see next section.

**Isolation Forest, extended to the full shortlist:** the real per-pixel Isolation Forest (v2, independent Pv/CPR/SERD/T-Ratio bands) previously only covered the primary candidate. Extended it to the other 6 shortlisted PSRs (`src/ml_pixel_anomaly_shortlist_pipeline.py`, reusing the same `/vsicurl/` windowed-remote-read technique and cached Drive URLs from last session). Mirrors exactly what was already done for hazard mapping's shortlist tier. Full writeup, plus why a regional pixel-level pass isn't planned (same multi-GB tradeoff as the earlier hazard-mapping decision), in `PRISM/docs/ML_METHODS.md`.

**OHRC data sourcing — found where to actually look.** PRADAN's product search requires already knowing the product ID, which is exactly the problem when you only have a target coordinate. Found: **CH2Browse** (`chmapbrowse.issdc.gov.in`) — ISSDC's map-based footprint browser, lets you visually locate the product covering a given lat/lon instead of guessing IDs. (It turns out the team already used this same tool successfully to resolve the DFSAR coverage blocker — see `PRISM/docs/CANDIDATE_ACQUISITION_SELECTION.md` Addendum 2 — the OHRC blocker is the same kind of problem and likely has the same fix, just not yet executed.) Full detail in `ML_METHODS.md` and a new Addendum 3 in `CANDIDATE_ACQUISITION_SELECTION.md`.

## OHRC abandoned, replaced with NASA LROC NAC — real optical coverage acquired (2026-08-23, same-day follow-up)

**OHRC is a confirmed dead end, not just a blocked one.** The user ran the exact CH2Browse workflow the previous section pointed to — 4°×4° box around the candidate — and got back "0 to 0 of 0 entries." South-polar Chandrayaan-2 OHRC coverage near this candidate genuinely doesn't exist; this isn't a search-technique failure to fix later.

**Pivoted to NASA's LROC NAC archive instead** — different mission (LRO, not Chandrayaan-2), public, no login, same `/vsicurl/`-style windowed-access philosophy already used for the LOLA DEM. Found a real, working coordinate-search tool at `data.lroc.im-ldi.com/lroc/search` (two non-obvious fixes were needed to make it actually return results: search the canonical host directly rather than the `wms.lroc.asu.edu` alias it redirects from, and submit every form field with its default value, not just the ones being filtered on — this old Rails app 500s or silently no-ops on a partial POST).

**Downloaded and pixel-verified real imagery for two candidates:**
- `SP_842420_0421060` (shortlisted): 0.93 m/px, 528.9 MB, 99.3% valid pixels.
- `SP_840980_0797630` (primary): 2.14 m/px, 264.5 MB, 98.7% valid pixels.

**A real false-positive caught mid-session, worth remembering:** the first "covering" frame found for the primary candidate used an axis-aligned lat/lon bounding-box test and looked like a match — a proper point-in-polygon test against the frame's true (rotated, diagonal) footprint corners showed it actually missed the candidate. This is the *third* time this exact mistake has shown up in this codebase near the pole (see `CANDIDATE_ACQUISITION_SELECTION.md` Addendum 2 for the DFSAR version of the same bug). The bad file was deleted; the real match (`M1524271502RC`) was found by re-testing with correct polygon containment.

**What this does and doesn't unblock:** `cnn_yolo_interface.py`'s "no OHRC scene covering the candidate" blocker is resolved (by replacing the imagery source, not by finding OHRC coverage). Its other blocker — no labeled boulder/hazard training data anywhere in the project — is untouched; that's the next real gate before any YOLOv8/CNN work. The downloaded frames are calibrated but not map-projected; `PRISM/src/lroc_nac_georeference.py` does an approximate GCP-based crop (~30m residual, explicitly labeled DERIVED/APPROXIMATE), not full SPICE/ISIS photogrammetry.

Full writeup: `PRISM/docs/CANDIDATE_ACQUISITION_SELECTION.md` Addendum 4, `PRISM/docs/ML_METHODS.md` YOLOv8 section.

**Correction, same day: the primary candidate's NAC frame turned out to be noise, not usable terrain data — caught by the user, not by this session.** The user looked at the actual preview PNG and asked directly whether it looked right — it didn't (flat gray texture, no visible features). Checking properly: adjacent-pixel spatial correlation was **−0.077** (real terrain runs 0.7–0.95+; this is a textbook noise signature), and mean pixel value (7.6) was smaller than its own noise std (15.3). The file was real and correctly geolocated, but I'd only verified integrity (non-corrupt, right size, right coordinates), not signal quality — a real gap in what "confirmed win" should have meant, worth remembering: **geolocation-correct is not the same claim as usable.** Physically, this candidate's PSR interior gets zero direct sunlight (already known from this project's own hazard mapping), and ordinary pushbroom cameras like NAC (or OHRC) don't have enough signal there.

**Fixed with NASA ShadowCam** — a camera ~200x more sensitive than NAC, built specifically to image PSR interiors. Found its real (JS-driven, reverse-engineered) coordinate-search API, decoded real WKB footprint polygons for true point-in-polygon containment (not another bounding-box false positive), found 25 verified-covering frames, windowed-read the best one directly from its properly map-projected Cloud-Optimized GeoTIFF (no full download, same `/vsicurl/` philosophy as the LOLA DEM) — and this time verified **0.994 adjacent-pixel correlation** before calling it done. That's real terrain signal. The shortlisted candidate's NAC frame was re-checked the same way and does hold real signal (0.423 correlation) — no replacement needed there.

Full corrected writeup: `PRISM/docs/CANDIDATE_ACQUISITION_SELECTION.md` Addendum 5.

## The "no labeled training data" blocker: found a real dataset, then the user rejected it (2026-08-23) — SUPERSEDED, see below

User's instruction: find somewhere on the internet where south-pole/lunar boulder mapping has already been done, even partially, rather than starting from raw pixels. Found and verified real: **BoulderNet / YOLOv8-BeyondEarth** (Prieur et al. 2023, JGR Planets), a peer-reviewed, published, YOLOv8-format labeled boulder dataset. Downloaded from Zenodo (601.4 MB, no login, byte-exact match). Checked directly rather than trusted from the abstract: **93.6% of the training images (3,703 of 3,958) are real LROC NAC lunar imagery**, not a token lunar subset of a mostly-terrestrial set. Verified the labels themselves are real by rendering actual polygon annotations over an actual training image and visually confirming they trace real boulders.

**One overclaim caught and corrected within the same research pass:** a companion record was first reported as containing trained model weights; checked directly and it's the training/prediction code only, no `.pt` file. There's no shortcut to a ready-to-run model — training is still required — but the blocker that made training impossible (zero labels anywhere in the project) is fully resolved. Local training is feasible: this machine has PyTorch with Apple MPS GPU support, confirmed working.

**Superseded same day: the user reviewed the dataset and rejected it** ("the bouldernet doesnt seem right to me, please get rid of that completely from the directory"). Deleted entirely — `data/raw/boulder_net/` (original + filtered copy, ~1.8GB) and the verification image. It was never committed (gitignored `data/raw/`), so removal is complete and clean. The "no labeled data" blocker is open again. Priority also shifted, same conversation: build real 3D terrain models of the candidate regions (real LOLA DEM + real ShadowCam/NAC imagery) for the frontend, ahead of automated boulder detection — see the section below.

Full writeup: `PRISM/docs/ML_METHODS.md` YOLOv8 section.

## Real 3D terrain visualization — first version shipped, then corrected twice on user review (2026-08-23)

`frontend/src/components/visualizer/TerrainVisualizer.tsx` (used on Ice Detection) previously derived mesh height from a fabricated Pv-based formula. First fix: real LOLA DEM elevation (same 6.6km window as the existing real Pv/CPR/ice-likelihood evidence grid) drives height instead — verified real via two independent cross-checks (identical candidate coordinates land on the identical projected point across two separately-run scripts; a fresh, uncached single-pixel DEM read at the exact candidate coordinate vs. a point 550m away vs. unrelated locations shows real, spatially-coherent, non-fabricated values).

**User review caught two more real problems, fixed same session:**
1. Asked for concrete proof the DEM data was really from this candidate (reasonable, given the earlier NAC false-positive) — answered with the cross-checks above, not just an assertion.
2. Asked whether photos were even needed for the model (they weren't — the model is DEM elevation + real ML color data, no photos involved; this was under-communicated the first time).
3. The render itself was too zoomed in, too dark/flat-colored, and the rover-path lines looked disconnected from the crater surface.

**Rebuilt properly:** `PRISM/src/real_terrain_grid_pipeline.py` now also extracts a wide-context real elevation window (18km, 900×900px native, downsampled to 120×120) alongside the original narrow one. The wide grid drives terrain height everywhere (single continuous real surface, no seam). The real 6.6km ice-likelihood evidence grid is blended in as color **only within its own true covered footprint** (bilinear-sampled against real-world coordinates shared by both grids, since both were extracted from the same candidate center) — a thin white outline marks that boundary honestly instead of implying the evidence covers more ground than it does. Base terrain color is a real elevation-based hypsometric palette, not a flat data-viz color. Rover paths (a real DERIVED Pareto path-planning output, not fabricated, but expressed in scene-relative not absolute coordinates) now sample the real elevation grid to sit correctly on the surface instead of floating at a fixed height. Camera pulled back to frame the bigger area. Iterated once more on lighting/color balance after the first attempt rendered too dark to read.

**Cleanup, per user request:** all NAC crop artifacts (both candidates) and `lroc_nac_georeference.py` removed — fully superseded by ShadowCam, which is higher quality and already properly map-projected. See `ML_METHODS.md`.

Still primary-candidate-only; extending to the other 6 shortlisted candidates (which all have verified real ShadowCam coverage already) is a natural next step if wanted.

## What's next (keep this list current)
- [ ] Optical hazard detection (boulder/rock CV) — imagery blocker resolved (NASA ShadowCam confirmed real for all 7 shortlisted candidates, see below), labeling blocker is open again: BoulderNet was downloaded, verified, filtered for Earth-imagery contamination, then rejected by the user and deleted entirely (2026-08-23). No trained detector exists or is in progress. Deprioritized in favor of 3D terrain reconstruction (below) until a labeling approach is decided.
- [ ] 3D terrain reconstruction for the frontend — new priority (2026-08-23). Combine real LOLA DEM elevation (already used for hazard mapping) with real ShadowCam/NAC imagery (confirmed real this session, all 7 shortlisted candidates) into an actual 3D terrain model per candidate, so frontend maps/animations show real Moon geometry instead of synthetic placeholders. Not yet started — see `ML_METHODS.md` for status.
- [ ] Feed real Module 2 hazard scores into Objective 3 (landing site scoring) and Objective 4 (rover A* cost grid) — both are currently illustrative/derived models, not yet reading real terrain hazard
- [ ] Wire the shortlist-wide Isolation Forest results (`PRISM/outputs/objective1/ml/shortlist/`) into the frontend, same as the shortlist hazard data was wired into `SouthPoleMap`/`prismDemoData.ts`
- [ ] `PRISM/docs/PROJECT_EXPLAINED.md` (124 lines, plain-English + the honest validation-failure finding) and root `PROJECT_GUIDE.md` (632 lines, full team/stack/glossary) both function as "explain PRISM from scratch" documents with real overlap. Not merged this pass — they emphasize different things (PROJECT_EXPLAINED leads with the humbling `REFERENCE_PROJECT_COMPARISON.md` validation result; PROJECT_GUIDE has the team/role breakdown PROJECT_EXPLAINED lacks) and merging them well needs a content judgment call, not a mechanical one. Flagging for whoever picks this up next.
- [ ] `CandidateComparisonChart` / `CandidateTimeSeriesChart` still read from `SYNTHETIC_CANDIDATES` / `SYNTHETIC_TIMESERIES` — could be upgraded to the real 7-candidate shortlist data now that it exists, dropping the synthetic map candidates but keeping the (clearly-labeled) synthetic time series, since the pipeline only has one real acquisition per candidate, not a real time series
- [ ] Regional overview currently reports per-PSR hazard only for the 336 PSRs with existing radar coverage (reusing Objective 1's candidate table) — could be extended to all 653 catalogued PSRs if useful
