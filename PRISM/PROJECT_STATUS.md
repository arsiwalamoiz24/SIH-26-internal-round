# PRISM — Project Status Audit

**Audit date:** 2026-08-22
**Audit type:** Read-only. No notebooks, data, or code were modified, executed, or deleted as part of this audit.
**Audited artifacts:** the 5 notebooks under `PRISM/notebooks/`. `PRISM/data`, `PRISM/doc`, `PRISM/outputs`, `PRISM/src`, `PRISM/tests` are all **empty directories** — there is currently no code or data in this repository outside the notebooks themselves. None of the notebooks contain markdown cells; every notebook is pure code with inline `#` comments, so there is no in-repo narrative documentation of intent beyond what the code and print output show.

All data paths in every notebook point to Google Drive (`/content/drive/MyDrive/...`), i.e. Google Colab. Nothing is locally reproducible from this repository alone — the underlying DFSAR, Y4R, CPR, PSR, OHRC and DEM products all live outside the repo.

---

## 0. Executive summary

- **The candidate `SP_840980_0797630` is real and reproducible.** It falls out of a rule-based Pv/PSR screening pipeline run against actual ISRO PDS4 Chandrayaan-2 DFSAR L4 (Y4R) and L3C (CPR/SERD/T-Ratio) products, cross-checked against the LRO/LOLA South Pole PSR catalog. The same numbers reproduce identically in all three notebooks that touch it.
- **The DOP-from-raw-DFSAR investigation is genuine, careful, byte-level reverse engineering** of the L0A raw product — and it correctly avoids computing DOP from the Y4R EVN/VOL/ODD/HLX components, per instruction. But it is run on an arbitrary, non-geolocated 25×1024-pixel patch from the first 100 lines of an unrelated raw acquisition (0.008% of the product), produces three different DOP formulations disagreeing by ~0.08, and the phase-calibration step is explicitly self-labeled by the author as non-final. This is **EXPERIMENTAL**, not implemented science.
- **One notebook is a mislabeled duplicate.** `OHRC data analysis(pure Physiscs).ipynb` is byte-identical (verified by hash) to `objective1_y4r_polarimetry.ipynb.ipynb`. It contains **zero** OHRC content despite its name.
- **The real OHRC notebook (`ohrc.ipynb`) never establishes geolocation or overlap itself** — its own print of the calibrated-product XML is truncated before reaching the footprint block. This audit re-read the full, untruncated XML directly from the saved notebook file and found the scene's corner coordinates lie between −89.22° and −89.93° latitude — a narrow strip centered on the pole, ≈22 km × 2.6 km. Candidate `SP_840980_0797630` sits at −84.098°, ≈179 km from the pole. **Confirmed: this OHRC scene does not overlap the candidate, its approach region, its PSR, or the LOLA terrain window.** It must not be used for candidate-specific optical hazard analysis. See §3.4.
- **The terrain notebook (`obj2 (1).ipynb`) never finished running its own core deliverable** — the candidate-specific slope crop/hazard map/statistics have no captured output in the saved notebook. It also has a copy-paste bug (wrong zip file referenced) that makes its CPR/SERD numbers non-reproducible from a clean run, even though stale-looking successful output is displayed.
- **Isolation Forest, YOLOv8, and CNN are all 100% absent from the codebase.** Nothing beyond percentile-threshold rules and manual PSR-vs-surroundings differencing has been implemented. No labeled data exists anywhere.
- **FastAPI, PostGIS, Next.js, Deck.gl, Three.js, and A\* routing do not exist anywhere in the repository.** This is 100% future architecture.

---

## 1. Candidate SP_840980_0797630 — origin and reproduced statistics

**Origin notebook:** `objective1_dfsar_validation.ipynb.ipynb` — this is the cleanest, self-contained derivation (31 cells, no dead ends, no unresolved errors). The identical candidate-generation logic (DFSAR/Y4R ingestion → Pv → PSR-gating → candidate table → shortlist → CPR/SERD/T-Ratio comparison) is **copy-pasted as a shared preamble** into `objective1_y4r_polarimetry.ipynb.ipynb` (its first ~64 cells) and into `obj2 (1).ipynb` (its first ~22 cells). All three reproduce identical numbers for the candidate, confirming internal consistency.

**Screening pipeline:**
1. Load Y4R L4 mosaic (`evn`, `vol`, `odd`, `hlx` GeoTIFFs; 24181×24794 px, float32, `Moon_2000_South_Pole_Stereographic` CRS).
2. Compute `Pv = vol / (evn+vol+odd+hlx)` (Yamaguchi volume-scattering fraction) at 1500-px overview resolution.
3. Download the LRO/LOLA South Pole PSR shapefile (`NAC_POLE_PSR_SOUTH.ZIP` → `LOLA_PSR_75S_120M_82S_060M_5KM2_FINAL`, 653 polygons) live from `pgda.gsfc.nasa.gov`; rasterize as a mask over the same grid.
4. Rank all 336 PSRs that have any radar coverage by fraction of pixels in the top-decile ("high") Pv tier.
5. Shortlist 7 candidates for full-resolution follow-up: `SP_832640_0090770, SP_830080_0535120, SP_842420_0421060, SP_817950_1586580, SP_840980_0797630, SP_819860_1568660, SP_809570_2454450`.
6. For the shortlist, re-extract full-resolution Pv, CPR, SERD, T-Ratio windows (1 km buffer around each PSR polygon) and compare PSR-interior vs. local-surroundings means.

**Reproduced statistics for `SP_840980_0797630`** (lat −84.098°, lon 79.764°, area **14.234 km²**, from the LOLA PSR shapefile):

| Metric | PSR interior | Local surroundings | Difference |
|---|---|---|---|
| Pv (overview, 84 px, top-decile fraction 0.738) | — | — | ranked #6 of 7 shortlisted |
| Pv (full-res, n=22,810 valid px, window 265×253 px) | mean 0.507, median 0.549 | mean 0.426 (n=44,235) | **+0.081** |
| CPR | 0.630 | 0.532 | **+0.099** (7.33% of PSR px have CPR>1) |
| SERD | 0.636 | 0.692 | −0.056 |
| T-Ratio | 0.651 | 0.531 | **+0.121** |

Interpretation shown in-notebook: elevated Pv, elevated CPR (with a non-trivial CPR>1 fraction), and elevated T-Ratio inside the PSR relative to its immediate surroundings are the qualitative signature the screening treats as ice-favorable; SERD is *lower* inside the PSR here, which is not obviously consistent with a simple "rougher = icier" narrative and is not reconciled in any notebook. No statistical significance testing (no p-values, no multiple-comparison correction across the 7-candidate shortlist) is performed anywhere.

---

## 2. Component status table

| Component | Status | Notes |
|---|---|---|
| DFSAR ingestion (raw L0A + Y4R L4 + CPR L3C) | **WORKING** | Real ISRO PDS4 products, sizes/dims/CRS all verified in-notebook; Colab-only paths, not portable |
| Y4R decomposition (Pv from evn/vol/odd/hlx) | **WORKING** | Standard formula, computed at both overview and full-res |
| Pv | **WORKING** | See §1 |
| PSR screening | **WORKING** | Real LOLA PSR shapefile (653 polygons), correctly rasterized/aligned |
| Local-control (surroundings) analysis | **WORKING** | PSR-vs-surroundings differencing implemented for Pv/CPR/SERD/T-Ratio; no significance testing |
| CPR | **WORKING** (screening notebook) / **PARTIALLY WORKING** (`obj2`, see §3.3) | |
| SERD | **WORKING** (screening notebook) / **PARTIALLY WORKING** (`obj2`) | Large NaN fraction in raw SERD product, not fully explained |
| T-Ratio | **WORKING** (screening notebook) / **PARTIALLY WORKING** (`obj2`) | |
| DOP (from raw DFSAR) | **EXPERIMENTAL** | Real byte-level reverse engineering of raw L0A; correctly avoids Y4R components; but non-geolocated 25×1024 patch, 3 disagreeing formulations, calibration self-labeled non-final. See §3.2 |
| Isolation Forest | **MISSING / PLANNED** | Zero occurrences in any notebook |
| OHRC ingestion | **PARTIALLY WORKING** | One product (2023-08-20 bundle) corrupted/truncated; a second, different-date product (2025-10-10) opens and dimension-verifies correctly |
| OHRC geolocation | **SCIENTIFICALLY UNVERIFIED IN-NOTEBOOK, RESOLVED BY THIS AUDIT** | Notebook's own XML print is truncated before the footprint block. This audit read the full XML directly: scene corners −89.22°…−89.93° lat — **confirmed does NOT overlap** SP_840980_0797630 (−84.098°, ≈179 km away). See §3.4. |
| YOLOv8 | **MISSING / PLANNED** | Zero occurrences; no labeled boulder/hazard data exists |
| CNN | **MISSING / PLANNED** (correctly not built) | Zero occurrences; no ground-truth ice labels exist — consistent with instruction not to fabricate a supervised classifier |
| LOLA DEM | **PARTIALLY WORKING** | Real 20 m/px South Pole products downloaded from NASA PGDA: `LDSM_80S_20MPP_ADJ.TIF` (pre-computed slope map) and `LDEM_80S_20MPP_ADJ.TIF` (raw elevation). Slope download capped at 18% in the saved notebook state; **the elevation DEM (`LDEM`) is downloaded but never opened or referenced anywhere downstream** — it is dead weight in the notebook as saved |
| Slope | **SCIENTIFICALLY UNVERIFIED / INCOMPLETE** | **Not computed by the notebook at all** — `slope_crop = src.read(1, window=window)` reads a value directly from NASA's pre-baked `LDSM` slope product; there is no in-house slope algorithm (no `np.gradient`, no Horn's method, no GDAL/richdem call). No candidate-specific slope output was ever produced in the saved notebook (DEM incomplete); thresholds (<10° safe / 10–20° caution / >20° hazard) are explicitly self-labeled "crude" by the author |
| Roughness (terrain, distinct from SERD) | **MISSING** | Not computed anywhere in `obj2`. Would require the elevation DEM (`LDEM`), which is downloaded but currently unused — see LOLA DEM row |
| Landing-site scoring | **MISSING** | No composite score combining radar + terrain + optical exists anywhere |
| A* routing | **MISSING** | Zero occurrences anywhere in the repo |
| FastAPI | **MISSING** | Zero occurrences anywhere in the repo |
| PostGIS | **MISSING** | Zero occurrences anywhere in the repo |
| Next.js | **MISSING** | Zero occurrences anywhere in the repo |
| Deck.gl | **MISSING** | Zero occurrences anywhere in the repo |
| Three.js | **MISSING** | Zero occurrences anywhere in the repo |

---

## 3. Notebook-by-notebook detail

### 3.1 `objective1_dfsar_validation.ipynb.ipynb` (31 cells, all code)

**Purpose:** Ground-truth DFSAR/Y4R/PSR ingestion, Pv/CPR/SERD/T-Ratio candidate screening. This is the origin of `SP_840980_0797630`.

**Inputs (Google Drive, Colab-only paths under `/content/drive/MyDrive/datasetisro/`):**
- `ch2_sar_nrxl_20251025t211236510_d_fp_d18.zip` — raw L0A-RAW quad-pol DFSAR product, 2025-10-25 acquisition, product_id 2575411, 1.2 GB zip / 2.72 GB `.dat`. Inspected for size/XML only — not decoded into complex samples here (that's done in the Y4R notebook).
- `ch2_sar_ndxl_20250630my4rspwest_d_fp_xxx.zip` — L4 Y4R mosaic (`evn`/`vol`/`odd`/`hlx`), 4.59 GB, 24181×24794 px float32.
- `ch2_sar_ndxl_20250630mpcpspwest_d_fp_xxx.zip` — L3C CPR/SERD/T-Ratio mosaic, same grid.
- `NAC_POLE_PSR_SOUTH.ZIP` — downloaded live over HTTP from `pgda.gsfc.nasa.gov`, 653 PSR polygons.

**Outputs:** candidate table (336 PSRs with radar coverage, ranked), 7-candidate shortlist, full-res Pv/CPR/SERD/T-Ratio comparisons, RGB Y4R + Pv-anomaly plots for 3 candidates.

**Errors:** none captured (`--- ERROR ---` absent throughout).

**Scientific limitations:**
- "High Pv" tier is a data-derived percentile (top decile of *this scene's* Pv distribution), not a physically anchored ice threshold from literature.
- Screening (overview, 1500 px) and full-res validation use different resolutions — a PSR ranked highly at overview resolution is not guaranteed to look the same at full res, and vice versa; no resolution-consistency check is performed.
- SERD has a large NaN fraction in places (debug cell reports 39,454/115,868 NaN for one shortlist PSR window) that is investigated but not explained.
- No significance testing on any PSR-vs-surroundings difference.

**Status: WORKING.** This is the most reliable notebook in the repository.

### 3.2 `objective1_y4r_polarimetry.ipynb.ipynb` (115 cells, all code)

**Cells 1–64:** re-derive the identical DFSAR/Y4R/Pv/PSR/CPR/SERD/T-Ratio pipeline as §3.1 (same numeric results), then begin raw `.dat` byte-structure exploration (XML re-inspection, header/payload boundary search across several candidate offsets) — this stretch is exploratory and doesn't reach a firm conclusion on its own; the conclusion comes later (STEP 8–14, see below).

**Cells 65–115 (labeled STEP 2–STEP 49) — the DOP-from-raw-DFSAR investigation.** This is the core of the requested "can DOP be computed from appropriate DFSAR data" inquiry, and it is the most scientifically substantive work in the repository:

- **Byte layout reverse-engineered** (STEP 8–14): per raw imaging line (2325 bytes total, from XML `Array_2D_Image` at offset 48158, 1,256,410 lines × 2325 samples), the notebook empirically finds a 46-byte fixed prefix, a variable header region ending at byte 141, a 2048-byte I/Q payload (`PAYLOAD_START=141` to 2189, matching `samples_per_echo_line=1024 × 2 bytes`), and a 136-byte constant `0x80` padding tail. This conclusion is derived methodically (per-byte uniqueness counts across 100 lines, fixed-prefix/fixed-tail detection) rather than assumed.
- **Polarization channel identification** (STEP 16–19): the 2048-byte payload is interleaved 4-way (every 4th complex line) into 4 candidate groups, each ~25×1024 complex samples. Groups are mapped to HH/HV/VH/VV by comparing each group's real/imag standard deviation against the XML's per-polarization `standard_deviation_real/imag`. Fit quality: HV, VH, VV match closely (within ~0.04–1.3 units); HH's std-dev matches only loosely (14.59 vs XML 12.50) and its bias-mean match is the weakest of the four. This is a **moderate-to-good but not perfect** confidence identification — the notebook does not attempt an alternative interleaving/ordering to see if a better fit exists.
- **Three separate DOP computations, disagreeing with each other:**
  1. Naive uncorrelated per-pixel Stokes from bias-corrected HH/VV alone (STEP 24) — explicitly labeled by the author *"Diagnostic only — NOT the final calibrated DOP"* — degenerates to exactly DOP=1.0 everywhere (a known artifact of computing Stokes parameters from single uncorrelated samples rather than a spatial covariance estimate).
  2. **Covariance-based (5×5 local window) linear-pol Stokes DOP** using bias-corrected HH/VV (STEP 27–33): single global value **0.629**; local map over 21,420 valid pixels: mean **0.638**, median **0.652**, std 0.126. Window-size sensitivity checked (3×3/5×5/7×7 all land in the 0.63–0.68 mean range, so the result is not wildly window-dependent). After an ad hoc phase correction (STEP 42–43, co-pol −50°, cross-pol −5°, explicitly labeled *"Diagnostic only: do NOT call this final calibration"*) the mean barely moves, to 0.638; after an additional ad hoc gain correction (STEP 44) it moves to 0.641.
  3. **Hybrid-pol DOP** from synthesized left-circular-Tx fields LH/LV (STEP 46–48): single value **0.557**; local map mean **0.571**, median 0.586 — noticeably different from the linear-pol result (≈0.08 lower).
  4. A 4×4 full-quad-pol eigenvalue "polarization purity" diagnostic (STEP 35) gives **0.643**, closer to but not identical to (2).
- **Calibration is unresolved:** measured co-pol (HH·VV*) phase offset is 50.3° and cross-pol (HV·VH*) offset is −5.0°, while the XML's `phase_orthogonality` values are much smaller (HH −5.3°, HV 3.1°, VH −3.4°, VV −1.1°) — the notebook applies an empirically-fit correction rather than deriving one from the XML fields, and never reconciles why the two disagree by an order of magnitude.
- **`polsartools` checked and not installed** (STEP 37); no vendor/documented Chandrayaan-2 DOP formula found anywhere in the dataset (STEP 38) — **the DOP formula used throughout is the notebook author's own construction from general Stokes-parameter theory**, not a verified ISRO/PDS formula.
- **Critical scale caveat:** every DOP number above is computed over the **first 100 raw imaging lines only** (≈0.008% of the 1,256,410-line product), split 4-way to a 25×1024-pixel patch. This patch is **never geolocated** — no lat/lon is computed for it anywhere in this notebook, and it comes from a different raw acquisition than the ice screening (2025-10-25) with no established relationship to `SP_840980_0797630`, its PSR, or the terrain window. This is a **methodology proof-of-concept**, not a site-specific result.
- No unresolved runtime errors.
- **Does not compute DOP from Y4R EVN/VOL/ODD/HLX components at any point** — correctly consistent with the project's current instruction.
- **No Isolation Forest, sklearn, or any ML anywhere in this notebook.**

**Status: DOP = EXPERIMENTAL.** Sound methodological direction and real cross-validation against XML metadata, but three internally-inconsistent formulations, unresolved calibration, and no connection yet to any actual candidate location.

### 3.3 `obj2 (1).ipynb` (34 cells, all code) — Objective 2 / Terrain

**Cells 1–22:** re-derive the same Pv/PSR/candidate-table pipeline (using a *different*, irrelevant raw DFSAR acquisition for the unrelated raw-data inspection — 2021-04-14, product_id 2121911 — which doesn't affect the Pv results since those come from the Y4R/CPR mosaics, not the raw product). Reproduces identical `SP_840980_0797630` statistics to §3.1.

**Cell 23 — reproducibility bug:** attempts to extract CPR/SERD/T-Ratio GeoTIFFs but `zip_path` is set to the **Y4R mosaic zip** (`ch2_sar_ndxl_20250630my4rspwest_d_fp_xxx.zip`) instead of the CPR zip (`..._mpcpspwest_...`) used correctly in §3.1 — an apparent copy-paste error. Only `Readme.txt`/`.xml` get extracted; no `.tif` layers.

**Cell 24:** explicit `"Error: File ... not found"` prints for `cpr`, `srd`, `trt`.

**Cell 25:** unhandled `RasterioIOError` traceback — on a clean re-run, execution stops here.

**Cells 26–29:** nonetheless display CPR/SERD comparison numbers **identical to §3.1's results**. Given cell 25's fatal error, these outputs can only be stale/leftover from an earlier kernel session (before the cell-23 path regression was introduced) — **the notebook as currently saved cannot reproduce these numbers from a clean run.** This is a genuine scientific-integrity/reproducibility flag, not just a cosmetic issue.

**Cell 30:** downloads real LOLA/LRO 20 m/px South Pole DEM products from `pgda.gsfc.nasa.gov` — `LDSM_80S_20MPP_ADJ.TIF` (**pre-computed slope map**, 3.5 GB) and `LDEM_80S_20MPP_ADJ.TIF` (raw elevation). Captured output shows the slope download halted at **18% (652 MB / 3.5 GB)** when the notebook was last saved; the elevation download has no captured output at all. **Important:** `LDSM` is NASA's own already-computed slope raster (PGDA product), not a DEM the notebook derives slope from — and `LDEM` (the actual elevation surface) is downloaded but **never opened or referenced again anywhere in the notebook**. So even though the code superficially resembles a DEM→slope pipeline, no slope algorithm exists in this repository at all; slope is just read as a pixel value from a NASA-supplied raster, and no elevation-derived product (roughness, TRI, elevation variation) is possible without first putting `LDEM` to use.

**Cell 31:** correctly reprojects the candidate (−84.098°, 79.764°) from geographic to the Moon south-polar stereographic projection via `pyproj` (matching the Y4R rasters' CRS) and sets up a 10×10 km crop window (5 km buffer) around it, then reads `slope_crop = src.read(1, window=window)` directly from `LDSM` — **but produces no captured print output**, consistent with the DEM file not having finished downloading.

**Cells 32–34:** plotting and thresholding code:
- Thresholds: safe <10°, caution 10–20°, hazard >20°, with the author's own in-line comment: *"crude thresholds - refine once you overlay actual PSR boundary"* — i.e., the notebook's own author already flags these as preliminary.
- **No captured output for any of these cells** — the actual slope statistics (% safe/caution/hazard) and hazard map for `SP_840980_0797630` were **never produced** in this saved notebook state.

**Status: INCOMPLETE.** DEM source and coordinate transform are legitimate and correctly implemented, but the notebook's core deliverable — a candidate-specific slope/hazard result — does not exist yet. Slope thresholds are self-flagged as preliminary by the original author; they must not be presented as validated mission thresholds (consistent with the brief).

**Not present anywhere in this notebook:** roughness, elevation-variation statistics, a terrain "cost" metric, or an accessibility metric. These are entirely unimplemented.

### 3.4 `ohrc.ipynb` (8 cells, all code) — the only genuine OHRC notebook

- **Cells 1–3:** `ch2_ohr_ncp_20230820T0559124374_d_img_n18_Bundle.tar` (2023-08-20 acquisition) confirmed as a valid POSIX tar via the `file` command, but `tarfile.open()` fails with `"unexpected end of data"` — **the bundle is truncated/corrupted**. This acquisition is abandoned without further investigation.
- **Cell 4:** switches to a different, already-available product — `ch2_ohr_ncp_20251010T0942085687_d_img_d18.zip` (**2025-10-10** acquisition, unrelated to the 2023-08-20 bundle) — extracts successfully: calibrated browse PNG, calibrated `.img`/`.xml`, geometry `.csv`/`.xml`, and `.oat`/`.oath`/`.spm`/`.lbr` calibration files.
- **Cells 5, 7:** print the calibrated-product XML. **As saved, the print is truncated before reaching the footprint/corner-coordinate block** — but this audit re-read the same XML in full (directly from the notebook's embedded output, bypassing the truncation) to independently verify the metadata checklist required for this audit:

  | Field | Value found in XML |
  |---|---|
  | Dimensions | 101,075 lines × 12,000 samples |
  | Data type / bit depth | `UnsignedByte`, 8-bit |
  | Byte order | Not applicable / not present — irrelevant for 1-byte samples |
  | Offset | `offset = 0` byte; `file_size = 1,212,900,000` B = lines×samples exactly (no header/trailer) |
  | Scaling / calibration | No `scaling_factor` / `value_offset` element found in the `Array_2D_Image` block, despite `processing_level = Calibrated` — the calibration transform (if any) is not exposed as simple linear DN scaling in this metadata block |
  | Resolution | `pixel_resolution = 0.22 m/pixel`; detector pixel 5.2 µm, focal length 2080 mm, TDI64, line exposure 162.1 ms |
  | Acquisition geometry | roll 26.67°, pitch 14.15°, yaw 0.024°, descending orbit, spacecraft altitude 85.71 km |
  | Illumination | sun_azimuth 149.77°, **sun_elevation −0.77°** (sun below local horizon), **solar_incidence 90.77°** — i.e. grazing/terminator lighting for this scene |
  | Projection | "Polar stereographic", area "South Pole" |
  | Scene footprint (System_Level / Refined_Corner_Coordinates, identical) | UL −89.219895°, 218.053507° · UR −89.228375°, 226.509641° · LL −89.928812°, 57.548965° · LR −89.877154°, 351.147086° |

  **Overlap check against `SP_840980_0797630` (−84.098°, 79.764°):** all four scene corners lie between **−89.22° and −89.93°** latitude — within 0.08°–0.78° of the pole (≈2–24 km, using 1° ≈ 30.3 km on the Moon). The candidate is at **−84.098°**, i.e. **≈179 km from the pole** (5.90° × 30.3 km/°). The scene itself is a narrow strip roughly 101,075 × 0.22 m ≈ 22.2 km (along-track) by 12,000 × 0.22 m ≈ 2.64 km (cross-track), centered on the pole — nowhere near wide enough to reach 179 km out to the candidate. **Conclusion: this OHRC scene does NOT overlap `SP_840980_0797630`, its approach region, its PSR, or the LOLA terrain window used in `obj2`.** This is a geometric certainty from the numbers above, not an inference.

- **Cell 8:** reads the raw `.img` as `uint8` (matching XML `data_type=UnsignedByte`) at declared dimensions **101,075 lines × 12,000 samples**; reshape succeeds exactly (1,212,900,000 px matches), confirming dimension/dtype metadata self-consistency. **No radiometric scaling/LUT application, no image display (`imshow`), and the `geometry_*.csv` (per-line/sample ground coordinates, which would give a finer-grained footprint than the four corners above) was never loaded or parsed.**
- No markdown cells anywhere in this notebook — zero author commentary.

**Status:** OHRC ingestion = **PARTIALLY WORKING** (one product corrupted; a second, calendar-unrelated product opens and dimension-verifies, and is metadata-complete per the checklist above). **OHRC geolocation = confirmed NO OVERLAP with the candidate** (by this audit, not by the notebook itself — the notebook never performs this check). Per the project brief, this scene must **not** be forced into candidate-specific optical hazard analysis. If OHRC-based hazard analysis is required for `SP_840980_0797630`, a **different OHRC scene covering −84.098°, 79.764°** must be located and acquired — this one does not qualify.

### 3.5 `OHRC data analysis(pure Physiscs).ipynb` — mislabeled duplicate

SHA-256 hash of a full text extraction (all cell source + all captured text/stream output) is **byte-identical** to `objective1_y4r_polarimetry.ipynb.ipynb` — same 115 cells, same code, same printed results, same DOP investigation. Despite the filename, **this notebook contains zero OHRC-related code or content** — no `.tar`/`.zip` bundle handling, no `.img` decoding, no optical imagery whatsoever. It should be treated as an accidental duplicate/mis-save of the Y4R notebook, not as independent OHRC work. `ohrc.ipynb` (§3.4) is the only genuine OHRC investigation in the repository.

---

## 4. ML status (explicit, per instruction)

| Technique | Status | Evidence |
|---|---|---|
| Isolation Forest | **PLANNED** | Zero occurrences of `IsolationForest`/`sklearn` in any of the 5 notebooks (verified by search across full text extractions of all notebooks) |
| YOLOv8 | **PLANNED** | Zero occurrences anywhere; no labeled OHRC boulder/hazard training data exists in the repo |
| CNN | **PLANNED**, correctly not built | Zero occurrences anywhere; consistent with the instruction not to fabricate a supervised ice classifier without ground-truth labels — no such labels exist anywhere in the repository |

All candidate ranking performed so far (§3.1) is **rule-based**: percentile tiering of Pv, and manual PSR-vs-surroundings mean differencing for Pv/CPR/SERD/T-Ratio. This is legitimate exploratory radar analysis, but it is not machine learning, and should not be described as such.

---

## 5. Summary answers to the audit questions

**1. What is already genuinely working:**
The DFSAR → Y4R → Pv → PSR-gated screening → CPR/SERD/T-Ratio local-control pipeline (`objective1_dfsar_validation.ipynb.ipynb`), producing the real candidate `SP_840980_0797630` from real ISRO/PDS4 + LRO/LOLA data, reproducibly across notebooks.

**2. What has been experimentally demonstrated:**
That DOP can plausibly be computed directly from the raw quad-pol DFSAR L0A product (not from Y4R components) via a self-reverse-engineered byte layout, cross-validated against XML calibration metadata — but only as a small-sample, non-geolocated, internally-inconsistent (3 formulations, ~0.08 spread) proof of concept, with calibration explicitly marked non-final by its own author.

**3. What is missing:**
Isolation Forest, YOLOv8, CNN, any ML at all; an OHRC scene that actually covers the candidate (the one currently ingested is confirmed pole-centered and does not overlap); an in-house slope algorithm (current "slope" is read verbatim from a pre-computed NASA raster); a completed candidate-specific terrain/slope result; roughness, elevation-variation, terrain-cost, and accessibility metrics (blocked on actually using the already-downloaded `LDEM` elevation file); landing-site composite scoring; A* routing; FastAPI/PostGIS backend; Next.js/Deck.gl/Three.js frontend.

**4. What data is missing:**
Nothing in `PRISM/data` (directory is empty — everything lives on the original author's Google Drive and is not in this repo). The obj2 slope-raster download (`LDSM_80S_20MPP_ADJ.TIF`) is incomplete (18%); the elevation raster (`LDEM_80S_20MPP_ADJ.TIF`) downloaded but is unused. No labeled ice/boulder/hazard ground truth exists anywhere. No PolSARtools or documented Chandrayaan-2 DOP formula was found. **A genuine gap: no OHRC scene covering `SP_840980_0797630` exists anywhere in this project** — the one scene that was ingested is a different, pole-centered acquisition (confirmed via full XML corner-coordinate read, §3.4). The OHRC geometry CSV (finer-grained per-pixel coordinates) for the ingested scene exists on disk per the notebook's own directory listing but was never opened — moot for this scene given the corner-coordinate math already rules it out, but would matter for whichever scene is used instead.

**5. What can be reused:**
The entire `objective1_dfsar_validation.ipynb.ipynb` pipeline as-is (candidate table, shortlist, screening logic). The raw-DFSAR byte-decoding logic from `objective1_y4r_polarimetry.ipynb.ipynb` (STEP 2–23) is solid and reusable for extending DOP computation to the actual candidate location. The coordinate-transform logic in `obj2 (1).ipynb` cell 31 (geographic → Moon south-polar stereographic) is correct and reusable. `ohrc.ipynb`'s `.img`-decode *method* (reading `UnsignedByte` per XML `data_type`, reshaping to XML-declared line/sample dimensions) is verified and reusable for whichever OHRC scene ends up covering the candidate — but the specific scene it was applied to here (`ch2_ohr_ncp_20251010T0942085687...`, 101075×12000) is confirmed not to cover `SP_840980_0797630` and should not itself be carried forward for candidate-specific work.

**6. What should be implemented next (audit does not prescribe a plan, but flags the natural next questions):**
Locating/acquiring an OHRC scene that actually covers `SP_840980_0797630` (the current one is confirmed not to, per §3.4 — this is not a "check later" item, it's a known gap now); completing the obj2 DEM download and actually running the candidate-specific slope crop/stats that the code already sets up; putting the already-downloaded `LDEM` elevation raster to use for roughness/TRI (currently dead weight); fixing the `obj2` cell-23 zip-path bug; deciding whether to extend the raw-DFSAR DOP method to a window actually covering `SP_840980_0797630`.

**7. Scientific risks identified:**
- **Reproducibility risk:** `obj2 (1).ipynb` displays CPR/SERD results that cannot be regenerated from its own saved code due to the cell-23 path bug — anyone re-running it will hit a `RasterioIOError`, not the numbers shown.
- **Mislabeled notebook risk:** the "pure Physics OHRC" notebook is actually the Y4R notebook; anyone trusting the filename would wrongly believe OHRC physics analysis has been done.
- **Unvalidated DOP formula risk:** no vendor/documented Chandrayaan-2 DOP formula was found; the formula in use is the author's own derivation from general SAR polarimetry theory and disagrees with itself by formulation (linear-pol vs. hybrid-pol vs. eigenvalue-purity all give different numbers on the same data).
- **Scale/geolocation risk:** the DOP results are not yet connected to any real candidate location — presenting the current 0.56–0.64 DOP numbers as characterizing `SP_840980_0797630` (or any specific PSR) would be scientifically unjustified.
- **Threshold risk:** the terrain notebook's own author labels the slope thresholds "crude" — they must not be presented as validated mission-safety thresholds, per the brief. Separately, "slope" in this project is currently a NASA-supplied raster value, not an independently computed/validated quantity.
- **Overlap risk — already realized, not hypothetical:** the OHRC scene currently in this project does **not** cover the candidate (confirmed, §3.4). If anyone assumes it does — e.g. because "we have an OHRC notebook" — and proceeds to optical hazard analysis "for `SP_840980_0797630`," that output would describe the wrong patch of the Moon (a strip within ~24 km of the pole, not the candidate at ~179 km from the pole).
