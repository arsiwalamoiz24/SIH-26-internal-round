# PRISM — Evaluation Script & Reference (2026-08-27)

**Team OUTLIERs | SIH26_76 | Domain: Space | Category: Software**

This supersedes `script.pdf` (round-1 era — written before almost everything
below existed) and updates `PRISM_Evaluator_Reference.pdf` (still excellent
and mostly current, but written *before* this session's work closed several
of the gaps it lists as open). Read this document top to bottom as your talk
track; the Q&A section at the end is your backup for anything an evaluator
throws at you.

**The single most important framing change from the old script:** round 1's
script said "one module built, three ahead of us." That's no longer true.
**All four modules are built and running on real data** — ice detection,
hazard mapping, landing-site selection, and rover-traverse planning. What's
still open is narrower and more specific (see Section 7), and you should say
so plainly rather than either overselling or underselling where you are.

---

## 1. Opening — Problem Statement

Say this almost verbatim; it's tight and it's real:

> "Team OUTLIERs, Team ID SIH26_76, Domain Space, Category Software. Our
> problem statement is detecting subsurface water ice at the lunar south
> pole using Chandrayaan-2 radar data, and turning that detection into an
> actual landing site and rover path — not just a map with a highlighted
> crater."

Then the *why*, in your own words but hitting these points:

- The Moon's south pole has craters deep and steep-walled enough that
  sunlight never reaches the floor — **Permanently Shadowed Regions
  (PSRs)**. At the resulting extreme cold — often below 110 K — water ice
  deposited over billions of years can stay physically stable instead of
  sublimating away into space, unlike almost anywhere else on the airless,
  sunlit Moon.
- That ice matters for a concrete, non-abstract reason: in-situ water can
  supply drinking water directly, and — split by electrolysis — hydrogen
  fuel and breathable oxygen, at a fraction of the cost of launching water
  from Earth. This is why ISRO, NASA, and other agencies are actively
  targeting the south pole right now (Chandrayaan-3 already landed nearby
  in 2023).
- The scientific difficulty: PSRs can't be photographed with ordinary
  cameras — there's no sunlight. Detection has to rely on instruments that
  don't need visible light, chiefly radar, which sends its own signal and
  reads the echo. But radar's classic ice signatures (elevated circular
  polarization, elevated volume scattering) are *also* produced by rough,
  rocky, non-icy terrain — so a naive threshold produces false positives.
- **The actual gap PRISM closes:** detection already exists as a research
  technique. What doesn't exist is an automated pipeline connecting "we
  found a radar anomaly" to "here's where you land, here's whether it's
  safe, and here's how a rover physically gets there." Three groups feel
  this gap directly: ISRO mission planners picking where Chandrayaan-4/5
  should land, planetary scientists deciding which of hundreds of shadowed
  craters to prioritize, and future ISRU engineers who need ice-location
  data before committing real mission resources.

---

## 2. The Four-Module Pipeline — all four are real now

State this plainly and specifically — it's your biggest update over round 1:

1. **Ice Detection** (Objective 1) — screen real Chandrayaan-2 DFSAR radar
   data across the whole south-polar cap, gate to real PSR polygons, rank
   candidates on four independent radar indicators. **Done.**
2. **Hazard Mapping** (Objective 2) — real NASA LOLA elevation data →
   slope, roughness (TRI), illumination, for all 7 candidates plus two
   external validation sites at their own true full extent. **Done.**
3. **Landing-Site Selection** (Objective 3) — score real candidate points
   outside the crater on slope, illumination, and proximity to the
   ice-evidence target, requiring a real ~85m safety-clearance disc around
   the point (not just one pixel) before accepting it. **Done, fed by real
   Module 2 output** — this is the item the old evaluator reference doc
   flagged as "illustrative, not yet wired to real hazard data." It now is.
4. **Rover Traverse Planning** (Objective 4) — real weighted A* search over
   the real slope/illumination/boulder-detection grids, with a real battery
   state-of-charge model checked against a 14-day mission budget. **Done.**

If asked "what changed since the last round," the honest answer is: modules
3 and 4 went from illustrative/derived placeholders to running on the
project's own real Module 1/2 output, and a real 3D frontend was built to
show all of it.

---

## 3. Datasets Used — in detail

Lead with this line: **"Every dataset here is real, either public or
accessed with our own legitimate ISRO credentials — nothing here is
synthetic or placeholder data."** Then walk the table (keep it visible if
you're presenting slides, or just narrate the rows that matter most):

| Dataset | Provider | What it gives us | Resolution | Access |
|---|---|---|---|---|
| Chandrayaan-2 DFSAR L4-MOSAIC (Y4R) | ISRO / PRADAN | evn/vol/odd/hlx scattering bands → Pv | 25 m/px, whole south-polar cap | Login-gated, ~4.6 GB |
| Chandrayaan-2 DFSAR L3C-MOSAIC | ISRO / PRADAN | Pre-computed CPR, SERD, T-Ratio bands | 25 m/px | Login-gated, ~3.6 GB |
| Chandrayaan-2 DFSAR raw L0A/L1A SLC | ISRO / PRADAN | Complex I/Q samples for self-computed DOP | Native swath | Login-gated, several GB/pass |
| LRO/LOLA PSR shapefile catalogue | NASA PDS / ASU | 653 real polygons marking every PSR floor near the south pole | Vector | Public |
| NASA LOLA DEM | NASA PGDA | Elevation → slope, roughness, illumination | 20 m/px | Public, windowed remote read |
| NASA ShadowCam imagery | NASA/KPLO archive | Real optical imagery *inside* permanently shadowed craters | ~1.7 m/px | Public |
| NASA Mini-RF Global Mosaic | NASA PDS Geosciences Node | Independent CPR/DOP/Stokes bands, cross-check | 128 PPD (~24–237 m/px) | Public |
| BoulderNet / YOLOv8-BeyondEarth | Prieur et al. 2023 (Zenodo) | Labeled lunar-boulder segmentation masks, training data | Native NAC-scale | Public |
| M3 / LCROSS literature sites | Li et al. 2018 (PNAS); Colaprete et al. 2010 (Science) | Independently confirmed ice-positive craters used as validation ground truth | Crater-level | Published papers |

**The technique that makes this feasible on ordinary hardware**, worth
saying explicitly if asked "how did you handle multi-gigabyte satellite
files": we never fully download them. GDAL's `/vsicurl/` virtual filesystem
issues HTTP range requests, pulling only the small pixel window actually
needed — e.g. a 10×10 km crop around a candidate — directly from the remote
server. Same technique for the LOLA DEM, the Mini-RF mosaic, and the real
ShadowCam frames found this session.

**New this session, worth mentioning if datasets come up:** we found real
ShadowCam coverage for the two external validation sites too (Faustini and
Cabeus) — 50 and 37 verified real frames respectively, via the exact same
search technique already used for the 7 candidates.

---

## 4. Machine Learning — in detail

Open with the honest framing that's actually your strongest card here:
**"No labeled 'this pixel is confirmed ice' dataset exists anywhere on Earth
for this problem. So we didn't fake one. We used machine learning exactly
where it's legitimately usable, and nowhere else."**

### 4.1 Isolation Forest — unsupervised anomaly detection

**What it is:** Isolation Forest is an unsupervised anomaly-detection
algorithm. Instead of learning "this is ice" from labeled examples (which
don't exist), it isolates data points that are statistically unusual
compared to the rest of a dataset — points that take fewer random splits to
separate from the crowd are flagged as anomalies.

**Two versions, and why we're careful about the difference:**

- **v1 (PSR-level):** features are `area_km2`, `px_with_radar_data`,
  `high_tier_fraction`, `moderate_plus_fraction` — one row per PSR, 336
  PSRs total. **We say plainly that this one is circular** — its features
  are derived from the same Pv computation already used to shortlist
  candidates, so it's a demonstration that the ML pipeline works, not
  independent evidence.
- **v2 (pixel-level) — the one that actually matters:** real, independently
  measured Pv, CPR, SERD, and T-Ratio at every pixel, in a 264×264 px window
  per candidate. This is **non-circular** — four separately-measured radar
  bands as independent features. Output: an interior-vs-surroundings
  separation score per candidate.

**Real per-candidate results** (from
`PRISM/outputs/objective1/ml/shortlist/shortlist_pixel_anomaly_summary.csv`):

| Candidate | Mean inside PSR | Mean outside | Separation |
|---|---|---|---|
| SP_840980_0797630 (primary) | 0.1938 | 0.1771 | +0.0166 |
| SP_832640_0090770 | 0.1834 | 0.1739 | +0.0095 |
| SP_809570_2454450 | 0.2166 | 0.1559 | **+0.0607** |
| SP_819860_1568660 | 0.2801 | 0.1826 | **+0.0975** |
| SP_842420_0421060 | 0.1892 | 0.1962 | −0.0069 |
| SP_817950_1586580 | 0.1726 | 0.1874 | −0.0148 |
| SP_830080_0535120 | 0.2097 | 0.1973 | +0.0124 |

If asked "is a positive separation of +0.017 for your primary candidate
actually meaningful," the honest answer is: it's real and it's positive,
but it's modest — two other candidates in the shortlist show a stronger
separation. Say that. It's exactly the kind of finding this project treats
as data, not something to quietly bury.

**Not yet done, say if asked:** Isolation Forest hasn't been run for the two
external validation sites (Faustini, Cabeus) yet — the evidence page shows
an honest "not run for this site" placeholder rather than a fabricated
number.

### 4.2 YOLOv8 — boulder detection

**What it is and why it's a *separate* question from ice detection:**
YOLOv8 (You Only Look Once, v8) is a real-time object-detection/segmentation
neural network. We use the `n-seg` (nano, segmentation) variant. This has
nothing to do with detecting ice — it detects boulders in optical imagery,
which matters for landing safety and rover-path obstacle avoidance.

**Training data — and a decision worth mentioning if asked about it:** we
needed real labeled lunar-boulder imagery to train this without fabricating
labels. We found **BoulderNet** (Prieur et al. 2023, published, peer-
reviewed, on Zenodo). A first pass of this dataset included non-lunar
(Earth/Mars-contaminated) imagery — we reviewed it, judged it unsatisfactory,
and **deleted it outright** rather than train on it. We then re-acquired a
properly filtered, lunar-only version: **3,719 training / 697 validation /
262 test images**, all genuine LROC NAC lunar imagery.

**Real, validated metrics:** mAP50 (box) = **0.551**, mAP50 (mask) =
**0.179**. Say these numbers exactly if asked — don't round them up.

**What's new this session, and directly closes a gap the old evaluator
reference doc flagged as "trained but not yet integrated":** we ran this
exact trained model against our own real ShadowCam crops, for every one of
the 9 sites (7 candidates + Faustini + Cabeus), extracting real pixel
bounding boxes and converting them to real-world coordinates via each
crop's own affine transform. Real detection counts: 17–591 per candidate,
and 294/278 for Faustini/Cabeus (found via a fresh real ShadowCam search
this session, since neither had any optical imagery before). These real
boulder positions now feed directly into the rover-traverse A* engine's
obstacle-avoidance cost.

### 4.3 Why not one bigger model for everything?

If asked "why not train a single deep model to just detect ice directly":
because that requires labels, and **no ground-truth ice label exists for
any pixel in this study area, at any resolution.** Building a supervised ice
classifier would mean inventing labels — which we explicitly refused to do.
Unsupervised anomaly detection (Isolation Forest) and object detection on a
genuinely different, real-labeled problem (boulders, via YOLOv8) are where
ML is actually legitimate here.

---

## 5. Terrain, 3D Visualization & the Real Rover Traverse Engine

This section is new relative to both old docs and directly answers the "how
did you make the 3D renders" question you asked me to prep for — see
Section 9 for the Q&A phrasing, but the substance is here.

**How the 3D terrain render is actually built, step by step:**

1. For each site, a real elevation window is pulled from NASA's LOLA DEM
   (`LDEM_80S_20MPP_ADJ.TIF`, 20 m/pixel, via the same `/vsicurl/` windowed
   read described in Section 3) — sized to each site's own real extent (a
   fixed ~5–9 km window for the 7 candidates; a much larger ~20.5–20.7 km
   window for Faustini/Cabeus, since their real craters are genuinely
   bigger and a fixed small window would have silently faked the rest of
   the surface).
2. That real elevation grid drives the height of every vertex on a 3D mesh
   in the browser — not a formula, not a guess. The crater's real,
   non-circular rim shape comes from the real PSR boundary polygon
   (`data/raw/psr_south/*.shp`, via a 360-direction ray-cast against the
   true polygon edges), not a synthetic circle.
3. The 2D scientific layers (hazard classification, slope, roughness,
   illumination, radar Pv/CPR/SERD/T-Ratio) are each individually cropped,
   real, per-metric images — not one squeezed multi-panel figure — draped
   onto the mesh or shown alongside it, scaled so their real-world footprint
   matches the mesh's own real-world size.
4. The rover path is a real weighted A* search (Section 2, module 4) over
   real slope/illumination/boulder-cost grids — every bend in that path is
   the algorithm actually avoiding something real, not a decorative curve.

**What DEM means, and what to do if asked to show it directly** — full
answer in the Q&A section below (5.x / Section 9); the short version: DEM =
Digital Elevation Model, a grid where every pixel stores real ground height
in meters, and you can open the exact real file we used in QGIS live if
asked.

---

## 6. Faustini & Cabeus — External Validation, Shown Honestly

Say this framing exactly, it's the load-bearing sentence for this whole
section: **"We featured two craters that are NOT among our own 7 screened
candidates, specifically because they already have independently-published,
externally-confirmed ice evidence — and we show our own real data for both,
including the parts that don't support ice, rather than only the favorable
numbers."**

- **Faustini** — real, published ice evidence exists (Sinha et al. 2026),
  but localized to two small sub-craters (F2, F3) that are a tiny fraction
  of Faustini's 664 km² PSR. Averaging our own radar metrics across the
  *entire* crater dilutes that real, localized signal into noise — which is
  exactly why Faustini's whole-PSR numbers come out negative on our
  evidence page. Re-running the identical method at F2/F3's exact published
  coordinates recovers a strongly anomalous signal, 2–5× larger than our
  own #1-ranked candidate. Both numbers are shown, with this explanation —
  not just the flattering one.
- **Cabeus** — real claim to fame is LCROSS physically detecting water
  vapor in the 2009 impact plume, not a radar signature. Our own DFSAR
  method, run both whole-PSR and targeted at the exact LCROSS coordinate,
  does *not* show an anomalous reading either way. That's a real, honestly
  reported negative result — it doesn't contradict LCROSS, it just means
  our specific radar method isn't what would have found Cabeus's ice on its
  own.

**If asked "why not just show these as proof your method works":** because
it doesn't, on the radar evidence alone — see Section 7. We show them on
their real external merit instead of fabricating a radar match, which was
an explicit decision made and re-affirmed twice this session when asked to
do otherwise.

---

## 7. Honest Findings & Limitations — say these plainly, don't bury them

This is the section every evaluator will probe, and the project's actual
strength is that it already has real, specific answers instead of
deflecting.

- **Control-site validation genuinely failed, twice, independently.** Our
  combined radar-evidence score ranked LCROSS Cabeus — the strongest
  confirmed ice site on the Moon — *below* Wiechert, a confirmed ice-free
  site. Twice, in two separately-run experiments.
- **A second, independent instrument reached the same conclusion.** Real
  Mini-RF radar + Diviner thermal data, run through a published
  multi-condition method (PM4W, Wang et al. 2025) with zero threshold
  tuning, classified **all 12 tested sites** — 7 candidates, Cabeus,
  Wiechert, Faustini, Shackleton, de Gerlache — **NON_ICE**. Every single
  one, 0% ICE, 100% NON_ICE.
- **DOP could not be reproduced against one published paper's numbers**,
  across eight separately tested calibration/processing hypotheses — most
  likely because that paper doesn't specify which physical radar channels
  its own formula is built from, not a bug on our side.
- **CPR's ice-specificity is genuinely contested in the literature** — Neish
  2011, Eke 2014, Fa 2018 all show rough rock and fresh-crater ejecta
  produce the same elevated-CPR signature ice does.
- **The primary candidate's own terrain is mostly steep crater wall**, not
  a flat floor — real LOLA data shows a mean interior slope of 22°, with
  ~79% of it over a 20° hazard threshold.

**The one line that ties all of this together, say it close to verbatim:**
*"None of this invalidates the engineering. The radar, terrain,
optical-imagery, ML, and now the rover-traverse pipelines all genuinely
work end-to-end on real data. What isn't yet established is that the
underlying radar metrics reliably distinguish ice from rough terrain — our
own multiple independent validation tests currently say they don't, and
we're reporting that plainly instead of polishing it away."*

---

## 8. Feasibility & Scalability

- **Real data access, not just citations**: every dataset above was
  actually opened and read. Most are free/public; Chandrayaan-2 DFSAR needed
  a real ISRO PRADAN account, which the team obtained legitimately.
- **Compute cost stays small** because of the windowed-read technique — a
  single-candidate hazard/terrain run completes in seconds; ML training ran
  on a local machine with consumer GPU acceleration (Apple MPS), confirmed
  working, not assumed.
- **Demonstrated scale-up path, tested not assumed**: all 336 radar-covered
  PSRs were screened at reduced resolution in under 35 seconds; only the
  top 7 were processed at full native resolution. A concrete timing study
  showed full native-resolution processing of the entire south-polar cap
  would take 2+ hours — the tiered approach was chosen specifically to
  avoid that cost.
- **Still open**: no live backend (FastAPI/PostGIS are still planned, not
  built) — the frontend reads pre-computed real JSON files rather than a
  dynamically queryable system. Say this plainly if asked; it's honest and
  it's a reasonable scope call for a hackathon timeline.

---

## 9. Anticipated Evaluator Q&A

Everything from the two source docs is still valid and worth re-reading in
full (`PRISM_Evaluator_Reference.pdf` Section 8 has ~25 more Q&A pairs on
CPR, DOP, SERD NaN values, etc. — nothing there has changed). Below are the
ones that are **new or changed** since that doc was written, plus the
3D-render/DEM questions you specifically asked to be ready for.

### On the 3D renders

**Q. How did you actually make the 3D crater renders — is that real data or
a stylized illustration?**

A. Real data, end to end. The mesh height at every point comes from a real
NASA LOLA elevation grid, fetched for each site's own real extent — not a
formula guessing at a bowl shape. The crater's outline comes from the real
PSR boundary polygon in NASA's own shapefile catalogue, ray-cast in 360
directions to get its true (non-circular) shape. The only thing that isn't
"real photographed pixels" is the small per-vertex surface jitter added for
visual roughness at a scale finer than the DEM's own 20m resolution — that's
labeled as texture, not shape, and doesn't affect any computed number.

**Q. What is a DEM, in plain terms?**

A. Digital Elevation Model — a grid where every single pixel stores the
real measured height of the ground at that point, in meters, relative to a
reference surface. Ours comes from NASA's LOLA instrument (Lunar Orbiter
Laser Altimeter, on LRO): it bounced laser pulses off the Moon's surface
from orbit and timed the return to measure height, repeatedly, building up
a global height map. Ours is the `LDEM_80S_20MPP_ADJ.TIF` product — 20
meters per pixel, south-polar region, adjusted/calibrated by NASA's own
Planetary Geodesy Data Archive (PGDA) team. Slope, roughness, and shadow
geometry are all *derived* from this one file — nothing else is needed to
compute them.

**Q. If we ask you to show us the raw DEM data right now, what do you do?**

A. Two good options, in order of how impressive/fast they are:

1. **Live in QGIS (best option, do this if you have a laptop and 2 minutes
   to prep beforehand):** QGIS can open the real file directly from NASA's
   server without downloading it, using the exact same `/vsicurl/` technique
   the pipeline itself uses. In QGIS: *Layer → Add Layer → Add Raster
   Layer*, then for the source URI paste:
   `/vsicurl/https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ.TIF`
   — it opens as a real grayscale elevation raster you can pan/zoom/click
   on to read real height values pixel by pixel. Practice this once before
   the demo so you're not fighting a slow network connection live.
2. **Show the already-exported real grids on disk** (no network needed,
   works offline): open any file matching
   `frontend2/public/assets/prism/elevation/*_real_elevation_grid_wide.json`
   — it's a plain JSON file with a real 120×120 grid of real elevation
   values in meters, plus the exact window size and candidate coordinates
   it was fetched for. You can literally scroll it open in a text editor
   and point at real numbers. There's also a plain single-panel PNG crop of
   the same data at `frontend2/public/assets/prism/elevation_only/{id}.png`
   or `panels/{id}_slope_only.png` for the derived slope layer, if a visual
   is faster than raw numbers.

**Q. Is the elevation data the same file for every candidate, or separate
downloads?**

A. Same underlying NASA file (`LDEM_80S_20MPP_ADJ.TIF`), a single ~terabyte-
scale global south-polar mosaic. We never download the whole thing — each
candidate gets its own small windowed read (a few MB) centered on its own
real coordinates, sized to its own real crater extent.

### On what's newly finished (say if asked "what's changed since round 1/2.1")

**Q. Is the rover traverse/landing-site module real now, or still
illustrative?**

A. Real now — this was the single biggest gap the last written reference
called out, and it's closed. The rover path is a genuine weighted A* search
over real slope, illumination, and real YOLOv8-detected boulder positions,
with a real battery state-of-charge model checked against a 14-day mission
budget, and a real ~85-meter safety-clearance requirement around the chosen
landing point (not just a single safe pixel).

**Q. How do you know the rover path isn't just going straight down a
slope?**

A. Because we specifically tested for that and fixed it. The router
evaluates the real *directional* slope along its actual heading — the same
physical mechanism that makes highway switchbacks work — not just the
steepest possible slope at a point. We verified this directly: at a
stricter 25° hard mobility limit, a naive isotropic-only router fails to
find a path at 5 of our 9 sites; the directional router succeeds at all 9,
with the real maximum climb along the path dropping substantially in every
case (e.g. our primary candidate: 24.4° → 14.5°) in exchange for a somewhat
longer route — the actual mathematical signature of a switchback, not a
tuned-to-look-good number.

**Q. Has YOLOv8 actually been run on your own imagery yet, or just
BoulderNet?**

A. Both now. It was trained and validated on BoulderNet (Section 4.2
numbers). This session, we ran the exact same trained model on our own real
ShadowCam crops for all 9 sites, extracting real per-boulder positions that
now feed directly into the rover-traverse obstacle-avoidance cost.

---

## 10. Closing line

Something close to this, adapted to your own voice:

> "That's where we are. All four modules of the pipeline are built and
> running end-to-end on real data — radar screening, terrain hazard
> mapping, landing-site selection, and rover-traverse planning. We validated
> our own method against known ice sites, found it doesn't yet reliably
> separate ice from rough terrain, and we're telling you that directly
> instead of hiding it. That's not a weaker project — it's a team that
> checks its own work before anyone has to ask."

---

## Appendix: what specifically changed vs. the two source documents

For your own reference, not something to read aloud — a direct diff of
what was stale in `script.pdf` and `PRISM_Evaluator_Reference.pdf`:

- `script.pdf` (round 1) said modules 2–4 were all still ahead of the team,
  Isolation Forest/YOLO were "roadmap items, not claiming them done," and
  the frontend didn't exist yet. **All of that is now done** — see Sections
  2, 4, 5.
- `PRISM_Evaluator_Reference.pdf`'s Section 5.2 ("What is not yet feasible")
  said landing-site/rover-traverse ran on an "illustrative/derived model,"
  and YOLOv8 was "trained but not yet integrated with the project's own
  real crater imagery." **Both are now closed** — see Sections 2 and 4.2.
- Both documents predate: the real 3D terrain frontend, the real ShadowCam
  search+extraction for Faustini/Cabeus, the real directional-slope
  switchback fix, the real ~85m landing-safety-disc requirement, and the
  real per-site full-extent terrain data for Faustini/Cabeus (previously
  silently faked past a ~9km radius for those two).
- Everything else in the evaluator reference PDF — the glossary, the
  dataset table, the honest-findings section (Cabeus/PM4W/DOP/CPR), the
  feasibility/scalability analysis — is still accurate and worth using
  as-is; it does not need to be re-read or re-verified before your
  evaluation.
