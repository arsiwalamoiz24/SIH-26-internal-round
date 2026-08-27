# PRISM — Current Status (2026-08-27)

This supersedes the ML/frontend/architecture gaps listed in `PRISM/PROJECT_STATUS.md`
(a 2026-08-22 read-only audit of the original notebooks — kept as-is, historical
record, do not edit). Since that audit, a real Python pipeline (`PRISM/src/`) and a
real Next.js frontend (`frontend2/`) were built. This doc is a snapshot of what
exists now, why key decisions were made, and where to look for detail. Every claim
below points at a real file — check it if in doubt.

---

## 1. Machine learning — no longer "planned", both implemented

The 2026-08-22 audit correctly found Isolation Forest, YOLOv8, and CNN all 100%
absent. That has changed:

### Isolation Forest (Track J-v2) — real, implemented
Per-pixel ice-likelihood scoring trained on real Pv/CPR/SERD/T-Ratio bands,
**independent of the screening metric** used to rank candidates (not circular).
A positive separation means pixels inside the PSR score higher on ice-likelihood
than the surrounding approach terrain in the same window.

Results (7 screened candidates — real, from
`PRISM/outputs/objective1/ml/shortlist/shortlist_pixel_anomaly_summary.csv`,
transcribed into `frontend2/src/data/prism.ts`):

| Candidate | Mean inside PSR | Mean outside | Separation |
|---|---|---|---|
| SP_840980_0797630 (primary) | 0.1938 | 0.1771 | +0.0166 |
| SP_832640_0090770 | 0.1834 | 0.1739 | +0.0095 |
| SP_809570_2454450 | 0.2166 | 0.1559 | +0.0607 |
| SP_819860_1568660 | 0.2801 | 0.1826 | +0.0975 |
| SP_842420_0421060 | 0.1892 | 0.1962 | −0.0069 |
| SP_817950_1586580 | 0.1726 | 0.1874 | −0.0148 |
| SP_830080_0535120 | 0.2097 | 0.1973 | +0.0124 |

Not yet run for Faustini or Cabeus — the evidence page shows an honest "not run
for this site" placeholder rather than a fabricated number for those two.

### YOLOv8n-seg boulder detector — real, implemented, now covers all 9 sites
Model: `PRISM/models/boulder_detector_yolov8n_seg.pt` (trained on BoulderNet real
lunar NAC imagery elsewhere on the Moon, box mAP50=0.551 per its own README — a
real domain gap exists running it on ShadowCam PSR crops, acknowledged, not hidden).

- 7 screened candidates: `PRISM/src/export_real_boulder_positions.py` — real
  pixel bounding boxes converted to real-world south-polar-stereographic meters
  via each crop's own affine transform, 17–591 detections per site.
- Faustini + Cabeus (new this session): `PRISM/src/shadowcam_featured_sites.py`
  found real ShadowCam coverage for both (50 and 37 verified frames respectively,
  via the real ASU/im-ldi PDS archive search already used for the 7 candidates),
  extracted real crops, then ran the same detector — 294 and 278 real detections.
  Output: `frontend2/public/assets/prism/pathfinding/{id}_boulders.json`.

CNN classifier remains correctly **not built** — no labeled ice/boulder ground
truth exists to train one without fabricating labels, same reasoning as the
original audit.

---

## 2. Radar/physics validation (PM4W, Cabeus/Faustini) — see existing docs

Not re-summarized here in full; see `PRISM/docs/PM4W_VALIDATION_RESULTS.md`,
`CABEUS_FAUSTINI_ICE_INDICATOR_PROFILE.md`, `DOP_GROUND_TRUTH_INVESTIGATION.md`.
One-line summary for anyone new: PRISM's own rigorous PM4W method (real Mini-RF
CPR+DOP+phase+backscatter + real Diviner temperature) classifies **all 12 tested
sites as NON_ICE**, including Cabeus (LCROSS ground truth exists there) — this is
reported honestly on the evidence page rather than suppressed or overridden.

### Why Faustini/Cabeus show negative/different whole-PSR values on the evidence page
This comes up because it looks inconsistent at a glance — it isn't:
- **Faustini**: real published ice evidence (Sinha et al. 2026) is localized to
  two small sub-craters, F2 (1100m) and F3 (700m) — together a tiny fraction of
  Faustini's 664 km² PSR. Averaging our radar metrics across the *entire* crater
  dilutes that localized signal into a mostly-ordinary floor's noise, which is
  exactly why the whole-PSR deltas come out negative. Re-running the identical
  method at F2/F3's exact coordinates (`PRISM/src/faustini_subcrater_pipeline.py`)
  recovers a strongly anomalous signal, 2–5× larger than PRISM's own #1-ranked
  candidate. Both numbers are shown on the evidence page now, with this
  explanation, instead of just the confusing whole-PSR number alone.
- **Cabeus**: its real claim is LCROSS's direct 2009 in-situ water detection in
  the impact ejecta plume, not a radar signature. Re-running PRISM's DFSAR method
  there (whole-PSR and targeted at the exact LCROSS coordinate,
  `PRISM/src/cabeus_targeted_pipeline.py`) does not show an anomalous reading
  either way — a real, honestly-reported negative result for this specific radar
  method at this specific site. It doesn't contradict LCROSS; it means DFSAR
  backscatter isn't the signal that would have found Cabeus's ice on its own.
  (A separate real Mini-RF S-band analysis does show elevated CPR at the exact
  LCROSS point, but that's traced to a documented non-ice fresh-crater-ejecta
  mechanism, Fassett et al. 2024 — also reported honestly, not claimed as ice.)

**Explicit decision, twice requested this session and declined both times:**
fabricating a positive ice signal for Faustini/Cabeus to "validate our other
findings" was not done. Both sites are instead featured prominently on their
real external merit (Sinha et al. 2026 for Faustini, Colaprete et al. 2010/LCROSS
for Cabeus), with PRISM's own real data shown as-is alongside.

---

## 3. Real rover-traverse engine (`frontend2/src/lib/traversePlanner.ts`)

Replaces a teammate's earlier hardcoded-spiral placeholder entirely. Real
weighted A* over real slope/illumination/boulder-detection grids, plus a real
battery state-of-charge model, checked against a hard 14-day mission budget.

- **Directional (switchback-aware) slope cost** — the key fix, per direct
  feedback that a purely isotropic slope model would make the rover "go
  straight down the slope, that is not realistically possible." The router now
  evaluates the actual along-heading grade (real elevation gradient dotted with
  the travel direction), not just the isotropic steepest-descent magnitude —
  the same real mechanism that makes mountain-road switchbacks work. Verified:
  at a **stricter** 25° hard mobility limit, purely-isotropic routing fails for
  5 of 9 sites, but directional routing succeeds for all 9, with the actual
  climb dropping substantially in every case (e.g. primary candidate 24.4°→
  14.5°, Cabeus 9.2°→5.4°) for a modestly longer path — the real signature of a
  switchback, not a tuned number.
- **Battery model**: real duty-cycle (bounded 4hr/day active drive window,
  matching how real rover missions actually operate, not continuous driving),
  real drain/charge differential, rover speed set to Curiosity's real documented
  max drive speed (0.14 m/s) after the crawl-pace default put most real routes
  over budget on distance alone.
- **Landing-site safety** (this session, per explicit feedback that the lander
  was sometimes selecting a point that "looks dangerous"): a candidate landing
  point must now have a real ~85m-radius safe disc around it (70–100m requested
  margin) — sampled at 8 perimeter points plus center, all real slope/crater-
  membership checks, not just the single candidate pixel. Verified against all
  9 sites: still finds valid outside-crater landing sites everywhere, no
  regressions.
- **Real pathfinding grids**: `PRISM/src/export_pathfinding_grids.py` (slope +
  illumination, derived from the real LOLA elevation grids, no new network
  reads) for all 9 sites, regenerated at full real extent for Faustini/Cabeus
  this session (see §4).

---

## 4. Frontend audit + fixes (this session)

Full detail in git history; summary of what was found and fixed:

- **Faustini/Cabeus 3D terrain was genuinely showing fake data for part of the
  mesh.** Real PSR polygon radius for both is ~15.8km, but their elevation grid
  and hazard/terrain crops were only ever fetched to 9000m/5000m — everything
  beyond that silently fell back to a synthetic bowl shape. Regenerated real
  LOLA elevation + hazard + terrain data at each site's actual full extent
  (`PRISM/src/regenerate_featured_sites_full_extent.py`, ~20.5km/20.7km).
  **Same bug independently found affecting the 6 non-primary screened
  candidates'** terrain texture (regenerated at a real 5000m buffer earlier in
  this session, but the frontend still assumed the old 3300m) — fixed too.
- **Real ShadowCam imagery for Faustini/Cabeus** — genuinely didn't exist
  before (one candidate's photo was even wrongly reused as a placeholder for
  Faustini). Found real coverage via the same validated ASU/im-ldi PDS search
  already used for the 7 candidates (`PRISM/src/shadowcam_featured_sites.py`),
  extracted, verified (adjacent-pixel correlation 0.94–0.99 — real signal, not
  sensor noise), and ran the real boulder detector on both.
- **Single-orbital-frame ShadowCam crops are real but small relative to
  Faustini/Cabeus's much bigger craters** (an orbital swath can't be widened
  the way a LOLA DEM windowed read can). The 3D texture math was silently
  stretching that small real patch across the whole mesh, implying full
  coverage it doesn't have. Fixed: the crop now renders at its true relative
  scale and position (`terrain/page.tsx` `CraterMesh`'s `textureHalfM`, no
  longer capped to always fill the mesh).
- **Duplicate/inconsistent data layer**: Faustini existed twice in
  `frontend2/src/data/prism.ts` (once with a shadowcam field wrongly pointing
  at the primary candidate's photo) — caused it to render twice as a map
  marker. Fixed; one canonical entry now.
- **Per-metric plots split out of multi-panel matplotlib strips.** Every
  composite (radar 4-panel, hazard 4-panel, terrain 3-panel) was a single wide
  image, squeezed into a small box on the evidence/terrain pages. New scripts
  (`PRISM/src/split_hazard_terrain_panels.py`, `split_radar_panels.py`) export
  each real metric (slope, roughness, illumination, TRI, Pv, CPR, SERD,
  T-Ratio) as its own crop for all 9 sites (72 files), used to build a proper
  grid layout on both pages instead of a stretched strip.
- **Evidence and terrain pages rebuilt** to one consistent layout for all 9
  sites (no separate "Featured Validation Sites" dropdown subsection — Faustini/
  Cabeus are regular rows, labeled `SP-XXXXXX Name` like everything else, at
  the top of the list); removed the misleading "False Color Composite" label
  (only 1 of the radar composite's 4 panels is actually false-color RGB;
  relabeled "DFSAR Radar Composite"); removed repeated generic placeholder text.
- **Candidates page**: clicking Faustini/Cabeus previously navigated away to
  `/evidence` instead of behaving like the other 7 candidates. Now selects them
  in place and shows their real info in the same detail panel/format.
- **Traverse page UI**: matched the site's shared design tokens (was a
  separate hardcoded neon dark-mode palette); removed the "Rover Operations /
  Rover Traverse Simulation" static header and the thin animated progress-bar
  line; added a live telemetry HUD (slope/battery/speed/illumination at the
  rover's actual current simulated position, from the real A* plan, not
  decorative); enlarged the telemetry-panel text (was 8-9px); zoomed the 3D
  camera out on both the terrain and traverse pages for better landing-zone
  context.

---

## 5. Known honest gaps (not fixed, flagged rather than hidden)

- Isolation Forest not run for Faustini/Cabeus (shown as "not run for this
  site", not a fabricated number).
- `IceLayer` (the light-blue ice-location overlay in the 3D traverse view)
  still uses a decorative sine-wave-edge circle, not the exact real PSR
  boundary shape — lower priority, not yet fixed.
- ShadowCam single-frame crops for Faustini/Cabeus cover a small fraction of
  their real crater (a genuine data limitation of a narrow orbital swath, not
  a bug) — rendered at true scale rather than stretched, but still small.

---

## 6. Where things live (quick index)

- Frontend: `frontend2/src/app/{evidence,terrain,traverse,candidates}/page.tsx`,
  data layer `frontend2/src/data/prism.ts`, traverse engine
  `frontend2/src/lib/traversePlanner.ts`.
- Real per-site assets: `frontend2/public/assets/prism/{panels,featured_shadowcam,
  pathfinding,elevation,psr_boundary,hazard_only,elevation_only,radar_only}/`.
- Pipeline scripts (all real, all reproducible, no fabricated data):
  `PRISM/src/{split_hazard_terrain_panels,split_radar_panels,
  regenerate_featured_sites_full_extent,shadowcam_featured_sites,
  export_pathfinding_grids,export_real_boulder_positions,radar_pipeline}.py`.
