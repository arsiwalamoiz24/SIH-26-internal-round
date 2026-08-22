## ADDENDUM 3 (2026-08-23): OHRC scene discovery — same problem, same fix, not yet done

This document is about finding the right **DFSAR** acquisition; the same discovery problem now blocks **OHRC** (the optical imagery needed for boulder/hazard detection — see `ML_METHODS.md` for the full YOLOv8 status). PRADAN's product search is hard to use for this because it requires already knowing the product ID/date — exactly what's unknown when you only have a target coordinate.

**Same fix that worked for DFSAR in Addendum 2 below applies here: CH2Browse (`chmapbrowse.issdc.gov.in`)**, the map-based footprint browser, lets you visually locate footprints over the candidate's lat/lon (−84.098°, 79.764°) instead of guessing product IDs. Note §4 below found this tool required an authenticated ISSDC session at the time it was first checked — but Addendum 2 confirms the team obtained legitimate authenticated PRADAN access this session, which should also unlock CH2Browse (same ISSDC login).

**Apply the same lesson learned the hard way in Addendum 2's step 3**: when checking whether a candidate OHRC scene actually covers `SP_840980_0797630`, use the label's true rotated footprint corners (`image_upper_left/upper_right/lower_right/lower_left_mapX/mapY`), not the loose axis-aligned bounding box (`upper_left/upper_right/lower_right/lower_left` without the `image_` prefix) — the latter gave a false-positive containment match for DFSAR and would likely do the same for OHRC. Confirm with a second independent check if the product has a geometry/grid CSV, same as the DFSAR resolution did.

**Status: not yet done.** This addendum documents where to look, not a completed acquisition. The OHRC scene currently in this project (`ch2_ohr_ncp_20251010T0942085687_d_img_d18`) remains confirmed NOT to cover the candidate (see `ML_METHODS.md`, `PROJECT_STATUS.md` §3.4).

---

## ADDENDUM 2 (2026-08-22, same-day follow-up): RESOLVED — covering acquisition found, confirmed, and downloaded

**User obtained legitimate authenticated PRADAN access this session.** Using it:

### Method

1. PRADAN's Map Browse spatial search (`chmapbrowse.issdc.gov.in`) was used to search DFSAR calibrated products near the candidate. This tool's AOI search returned a fixed pool of nearby products regardless of the exact query box size — useful for discovery, but its own matching logic is not precise enough to trust for final containment (confirmed empirically: identical result sets for a 0.4°×0.5° and a 1°×2.5° box).
2. All 602 manifest acquisitions' PDS4 labels were fetched directly (via the same `browsePathConstructor` + `DisplayLabel` API the map-browse UI itself uses) and screened for real containment.
3. **First screening attempt (WRONG, corrected):** used the label's loose axis-aligned `upper_left/upper_right/lower_right/lower_left` corners (the padded scene-envelope box). This flagged `ch2_sar_ncxl_20191106t114537878_d_fp_d18` as containing. That product (4.88 GB) was downloaded. The actual Level-1A Grid CSV then showed the true minimum distance from the candidate to any real data pixel in that scene is **~51 km** (nearest grid sample at the range-edge column) — confirmed via the label's `image_*` (true rotated footprint) corners at **~75 km**. **This was a false positive from using the wrong corner set**, not from bad data. The 4.88 GB file was deleted; nothing from it is used anywhere in this project.
4. **Corrected method:** re-screened all 602 acquisitions using the `image_upper_left/upper_right/lower_right/lower_left_mapX/mapY` fields — the PDS4 label's **true rotated data-footprint corners**, distinct from the padded envelope box. Ray-casting point-in-polygon test in the same Moon_2000_South_Pole_Stereographic projected coordinates used throughout this project.

### Result: 6 genuine hits (of 602)

| Acquisition | Station | Distance to nearest true corner |
|---|---|---:|
| `ch2_sar_ncxl_20220318t135736694_d_fp_d18` | d18 | 19.99 km |
| `ch2_sar_ncxl_20220414t203316934_d_fp_d18` | d18 | 15.49 km |
| `ch2_sar_ncxl_20220829t094032861_d_fp_d32` | d32 | 18.37 km |
| `ch2_sar_ncxl_20230404t115607693_d_fp_d32` | d32 | 14.88 km |
| `ch2_sar_ncxl_20230404t135410450_d_fp_d32` | d32 | 18.03 km |
| `ch2_sar_ncxl_20230915t094631520_d_fp_d32` | d32 | 13.71 km |

**Selected: `ch2_sar_ncxl_20220318t135736694_d_fp_d18`** (largest margin, and station d18 per task priority). **Confirmed a second, independent way**: its actual Level-1A Grid CSV's nearest per-pixel sample to the candidate is **91 meters** away, at sample index 5 of 9 (mid-swath, not an edge case).

### What was downloaded

`ch2_sar_ncxl_20220318t135736694_d_fp_d18.zip`, 1,920,035,453 bytes, via PRADAN Browse-and-Download (Table View), authenticated session. Contains Level-0 is NOT included — this zip bundles Level-1A SLI (complex, `ComplexLSB8`, the product used for DOP), Level-1B GRI, and Level-2 SRI, plus geometry/browse, for this single acquisition only. No other acquisition was downloaded in full.

### Candidate-specific DOP

See `docs/DOP_VALIDATION_RESULTS.md` "Candidate-specific DOP status — RESOLVED this session" for full results. Headline: **linear-pol (HH/VV) Stokes DOP mean 0.680, median 0.708**, 488,000 px, 0% NaN.

---

## ADDENDUM 1 (2026-08-22, same-day follow-up): primary-source SIS confirms the exact grid filename

The official CH2DFSAR PDS4 Data Product Archive SIS (`ch2_sar_pds_dp_archive_sis.pdf`, SAC/SIPG/MDPD/CH2/SAR/2018/04/03/v1.0) is now available locally (`C:\Users\radhe\OneDrive\Desktop\data\sarlta\document\`, part of the official `sarlta` PDS4 bundle). This is a **primary source**, not a third-party web summary, and it upgrades the confidence of everything in this document:

- **Table 5.12 (PDF p.34-35), full file-naming-convention token table**, confirms: mtbb token `c`=calibrated, `xl`=L-band -- so manifest's `ncxl` = Normal-orbit-phase + Calibrated + L-band, exactly as concluded below. `p`='g' = "gridded data products under geometry directory".
- **PDF p.47, a complete real worked example** (the SIS's own sample "Grid Product XML" label) gives, verbatim: `<file_name>ch2_sar_ncxl_20191019t011733462_g_sli_xx_fp_xx_d18.csv</file_name>` -- a Table_Delimited CSV, 4 fields (Latitude, Longitude, Slant range, incidence angle), 198,858 records. This is a **literal, direct confirmation** of the `..._g_sli_xx_fp_xx_<stn>.csv` pattern already used below -- not an inference from an abstract token list. (Table 5.12 separately lists a `prd=grd` code too; the worked example resolves that ambiguity -- the per-scene grid accompanying an SLI product keeps `prd=sli`.)
- **Section 5.3.9 (PDF p.32-33)** confirms the `geometry/calibrated/<YYYYMMDD>/` path structure already used below.
- Corroborated by arXiv:2104.14259 (DFSAR instrument team's own performance paper), already cited below.

**No change to the predicted filenames themselves** (`outputs/objective1/dop/acquisition_coverage_candidates.json` already used this exact pattern) -- this addendum only upgrades the evidentiary confidence from "web-summarized" to "primary-source, literal worked example," and is reflected in that JSON's `sis_evidence` and `naming_convention.confidence` fields. PRADAN access remains BLOCKED (re-checked this session, same login-wall finding, §6 below unchanged).

---

# CANDIDATE_ACQUISITION_SELECTION — Level-1A Grid-based acquisition selection for candidate DOP

**Date:** 2026-08-22 (updated, same-day follow-up to the prior BLOCKED session below `## Prior session (superseded findings)`)
**Result: STILL BLOCKED at containment testing, but the metadata-identification problem is now SOLVED for all 602 acquisitions.** The official CH2DFSAR SIS/user manual confirms the Level-1A Grid CSV that would let us test candidate coverage per acquisition, and confirms the manifest's 602 entries *are themselves* Level-1A calibrated products (no raw/calibrated filename guess needed). But PRADAN/ISSDC still requires an authenticated login to fetch even this small Grid file, and no login was attempted. Deliverable: an exact, minimal, 602-item manual download list, prioritized by station, in `outputs/objective1/dop/acquisition_coverage_candidates.json`.

---

## 1. Candidate coordinates

`SP_840980_0797630`, lat **−84.098°**, lon **79.764°**.

## 2. What changed since the prior session

The prior session (see `## Prior session` section below, preserved for the record) was blocked on two compounding problems:

1. No footprint metadata existed locally for any of the 602 manifest acquisitions.
2. It was **unclear whether the manifest's `ncxl`-coded entries corresponded to a raw (`nrxl`) product at all**, and no documented `ncxl`→`nrxl` filename mapping could be found — so even *if* footprint data were obtained, it was unclear what raw product to actually request.

This session resolves problem (2) directly, and narrows problem (1) to a single, precisely-named, small file per acquisition.

## 3. SIS evidence for the Grid file

Two independent official sources, both checked this session:

- **arXiv:2104.14259**, "Chandrayaan-2 Dual-Frequency SAR (DFSAR): Performance Characterization and Initial Results" (the DFSAR instrument team's own paper): *"Each pixel of a given slant image is tagged to a particular seleno-location, i.e., latitude/longitude, value using the slant range grid generated from the orbit attitude information, a digital elevation model (DEM) available at ~118.5 m spacing from the LRO Laser Orbital Laser Altimeter (LOLA) and radar parameters. Additionally, the latitude and longitude of the four corners of the footprint are provided in the header of the data file."*
- **CH2DFSAR User Manual v1.0** (`SAC/SIPG/MDPD/CH2/SAR/2020/12/23/v1.0`), the same publicly-hosted document already used in the prior session, this time read via its full OCR text (`archive.org` mirror, `OtherDownloads/DFSAR/ch2_dfsar_user_manual_v1.0_djvu.txt`, no login required):
  - *"Level-1A product consists of Slant range Image (SLI) in single look complex (SLC) format along with the label file in xml."*
  - Grid file described explicitly as: *"Grid Delimited Text (csv) ... It contains the lat./lon. information corresponding to each pixel of the image."*
  - A real directory-tree example in the manual shows the path **`geometry/calibrated/20191019/`** containing **`ch2_sar_ncxl_20191019t041710471_g_sli_xx_fp_xx_gds.csv`**, paired with data file **`ch2_sar_ncxl_20191019t041710471_d_sli_xx_fp_hh_gds.tif`** in the corresponding `data/calibrated/20191019/` path.
  - The manual's example acquisition (station `gds`, 2019-10-19, ~04:17 UTC) sits within minutes and the same station/date as two *actual* entries in our 602-item manifest (`ch2_sar_ncxl_20191019t041708323_d_fp_gds`, `ch2_sar_ncxl_20191019t101034146_d_fp_gds`) — consistent with the manual documenting a real or near-real product, not a fabricated one, and directly corroborating that this naming convention applies to acquisitions of the same vintage as our manifest.

**Also checked and ruled out as sources of a pre-built footprint index:** the archive.org mirror `chandrayaan-2-high-resolution-images-of-the-moon` (a partial PRADAN mirror) — confirmed via its metadata file listing to contain only the DFSAR *user manual* and a processing-software tool (`MidasV2`, `sarlta_v0.tar`), **no actual DFSAR scene products** (unlike its OHRC folder, which does mirror real product zips). So this mirror cannot substitute for PRADAN itself.

## 4. Resolving the ncxl question

The manifest's 602 entries are named `ch2_sar_ncxl_<timestamp>_d_fp_<station>`. The manual's own worked example uses the **identical `ncxl` token** for a Level-1A/SLC (calibrated) product. This means:

**The 602 manifest entries already ARE the Level-1A calibrated products.** No conversion from a raw (`nrxl`) filename is needed, and none is assumed — this directly satisfies the task instruction not to assume an `ncxl`→`nrxl` mapping, by making that mapping unnecessary: we go `ncxl` (data) → `ncxl` (its own accompanying grid), same processing level, same acquisition, same timestamp/station.

## 5. Predicted per-acquisition filenames

For manifest entry `ch2_sar_ncxl_<TS>_d_fp_<STATION>` (`<TS>` = `YYYYMMDDtHHMMSSFFF`):

| Product | Filename pattern | Path |
|---|---|---|
| Level-1A SLC image, per polarization | `ch2_sar_ncxl_<TS>_d_sli_xx_fp_<pol>_<STATION>.tif` (`pol` ∈ hh, hv, vh, vv) | `data/calibrated/<YYYYMMDD>/` |
| PDS4 label, per polarization | `ch2_sar_ncxl_<TS>_d_sli_xx_fp_<pol>_<STATION>.xml` | `data/calibrated/<YYYYMMDD>/` |
| **Grid (lat/lon per pixel)** | **`ch2_sar_ncxl_<TS>_g_sli_xx_fp_xx_<STATION>.csv`** | **`geometry/calibrated/<YYYYMMDD>/`** |

**Confidence:** the *pattern* is HIGH confidence (quoted verbatim from the official manual, one real worked example). The *per-acquisition instantiation* for each of the 602 timestamps is a **prediction** — substituting each manifest entry's own timestamp/station into the confirmed pattern — not independently verified by downloading any of these 602 specific files, because doing so requires the authenticated PRADAN session this task instructs not to bypass. Every record in the output JSON carries this caveat individually.

All 602 predicted Grid filenames/paths (plus the SIS evidence, naming-convention block, and station-priority ordering) are in:

**`outputs/objective1/dop/acquisition_coverage_candidates.json`**

## 6. Can PRADAN serve the Grid/XML alone, without the raw/large image?

Checked this session (`WebFetch`, no login attempted):

- `pradan.issdc.gov.in/ch2/` — the "Table View" data-access link points to `/ch2/protected/payload.xhtml` (the path itself is literally named `protected`); the portal's own FAQ states registration/login is required for Chandrayaan-2 Orbiter imaging payload data download. Unchanged from the prior session's finding.
- `chmapbrowse.issdc.gov.in/` (map-based browse/download) — no evidence of public/unauthenticated footprint or metadata query found on the landing page.
- **Selective (grid-only) download:** no public documentation was found describing a per-file download endpoint. The documented delivery unit is a single zip per acquisition (containing `data/`, `browse/`, `geometry/` subfolders after extraction — confirmed from the manual's directory-tree examples and the archive.org-hosted `sar_readme.txt`). So the smallest unit PRADAN is documented to offer is the **whole Level-1A product zip** (4 polarization TIFs + XML labels + grid CSV + browse image) — much smaller than the multi-GB Level-0 raw `.dat`, but not a byte-level grid-only fetch.

**Conclusion: BLOCKED.** Per task instruction, no login was attempted or bypassed.

## 7. Footprint containment testing

**Not performed — 0 of 602 acquisitions tested.** This requires the actual Grid CSV (or at minimum the 4-corner lat/lon from the SLI's XML label), and none is available without the blocked login. The containment method itself (proper 4-corner polygon test with antimeridian-aware longitude handling, not scene-center distance alone) is already implemented and validated against the two raw products we do have locally (`docs/DOP_VALIDATION.md`, `outputs/objective1/dop/candidate_coverage_check.json`) — it is ready to run the moment real Grid/XML data for any of the 602 acquisitions is obtained.

## 8. Manual download instructions (for the human operator)

**Exact PRADAN navigation path:**

1. Go to `https://pradan.issdc.gov.in/ch2/` and register/log in (free ISSDC account; login was not attempted by this task per instruction).
2. Navigate to the DFSAR ("SAR") payload product search (Table View, under the protected `payload.xhtml` search/listing page).
3. Search by acquisition date and ground station using the timestamp/station pairs in `outputs/objective1/dop/acquisition_coverage_candidates.json` (field `manifest_filename`, e.g. `ch2_sar_ncxl_20190922t032857034_d_fp_d18` → date 2019-09-22, station `d18`).
4. For each matching product, download the Level-1A (calibrated SLC) product zip — **not** the Level-0 raw product.
5. Extract only `geometry/calibrated/<YYYYMMDD>/ch2_sar_ncxl_<TS>_g_sli_xx_fp_xx_<STATION>.csv` (and its `.xml` label if present) — the `data/calibrated/.../*.tif` polarization images are not needed for this containment check and can be discarded to save space.
6. Parse the CSV's per-pixel lat/lon, determine the scene's bounding polygon (handling any antimeridian wraparound), and test whether (−84.098°, 79.764°) falls inside — the method already implemented for the two local raw products applies unchanged.

**Priority order (per task instruction to prefer `d18` where the manifest/product structure supports it):**

| Station | Count | Priority |
|---|---:|---|
| d18 | 367 | 1st (61% of manifest; largest single bucket) |
| d32 | 163 | 2nd |
| n18 | 47 | 3rd |
| gds | 11 | 4th |
| g26 | 9 | 5th |
| m65 | 3 | 6th |
| mad | 2 | 7th (last) |

**Honesty check on this ordering:** no geometric or orbital evidence was found this session linking ground-station code to candidate-coverage likelihood. `d18` is prioritized only because (a) the task explicitly asked for it and (b) it is the largest single bucket, so it maximizes the number of acquisitions tested per unit of manual download effort if no other signal is available. This is **not** a geometric pre-filter — all 602 acquisitions remain untested and any of them, in principle, could be the one covering the candidate.

The full, exact, 602-row priority-ordered download list (manifest filename → predicted Grid filename → predicted path → priority rank) is in `outputs/objective1/dop/acquisition_coverage_candidates.json`, field `acquisitions`.

## 9. What exact product we need next

The Level-1A calibrated Grid CSV (`g_sli`) — ideally together with the corresponding SLI XML label(s) for provenance — for enough of the 602 manifest acquisitions (starting with the `d18` subset per §8) to find at least one whose footprint polygon contains (−84.098°, 79.764°). Once found, the corresponding Level-1A SLC `.tif` polarization images (already in the same downloaded product zip) become the direct input for candidate-level polarimetric DOP — no raw Level-0 focusing/processing is required, since Level-1A is already a focused, complex-valued (SLC) image per the manual's own definition.

## 10. Limitations

- **Zero acquisitions have been footprint-tested.** Everything in §5–§8 is metadata identification and a download plan, not a coverage result.
- **All 602 Grid filenames are predicted, not verified**, against real downloaded examples for these specific acquisitions — the pattern is confirmed from one official worked example (different acquisition, same convention), not from any of the 602 acquisitions themselves.
- The manual's DPSIS (Data Product Software Interface Specification) document — which would authoritatively confirm this naming convention rather than relying on one worked example — was referenced by the manual but not itself located publicly this session.
- It remains possible (not confirmed) that no single one of these 602 acquisitions covers the exact candidate pixel — SAR strip acquisitions are narrow (the two raw products we do have locally are ~135 km long × ~2.6–4.85 km wide), and the manifest reflects whichever passes ISRO chose to include in the Y4R/CPR mosaic compilation, not an exhaustive coverage guarantee.
- Whether PRADAN, once logged into, exposes a lighter per-file/metadata browse (rather than only whole-zip download) remains unconfirmed from outside the login wall, exactly as noted in the prior session.
- d18 station-priority ordering is a practical heuristic (largest bucket + task instruction), not a geometric filter — see §8.

---

## Explicitly not done, per task rules

- Did not download any of the 602 acquisitions, or any full raw/calibrated product.
- Did not attempt to log into PRADAN or the Chandrayaan Data Explorer.
- Did not fabricate a footprint for any manifest acquisition — all 602 `footprint_bounds_deg` / `candidate_containment` fields are explicitly `null` / `"UNTESTED"`.
- Did not assume an `ncxl`→`nrxl` (calibrated→raw) filename mapping — instead confirmed the manifest entries are themselves Level-1A calibrated products, per the official manual's own worked example, removing the need for that assumption entirely.
- Did not calculate DOP.
- Did not use the 2025-10-25 raw or 2025-11-06 compact-pol products as substitutes (both remain confirmed non-covering, see §10 of the prior session below).
- Did not implement any ML.
- Did not use scene-center distance as a stand-in for real polygon containment — no containment test was run at all, precisely because no real corner/grid data exists locally for these 602 acquisitions.

---

## Prior session (superseded findings, preserved for the record)

*Everything below this line is the unmodified content of the earlier BLOCKED session's writeup. It remains true and is not contradicted by the update above — the prior session correctly established that no footprint metadata existed locally and that PRADAN requires login. This session's contribution is resolving the `ncxl`/`nrxl` filename-mapping question and identifying the exact Grid file to request.*

**Date:** 2026-08-22
**Result: BLOCKED at Step 3 (spatial filter).** No footprint metadata could be obtained for any of the 602 manifest acquisitions without an authenticated ISSDC/PRADAN session. Zero acquisitions were footprint-tested; zero were confirmed or rejected on geometry. No download target can be named yet. Full evidence below.

### 1. Candidate coordinates

`SP_840980_0797630`, lat −84.098°, lon 79.764°.

### 2. Manifest source

Two files, byte-identical 602-item sets, extracted this session (no download -- read via Python `zipfile` from the already-local original zip archives in `C:\Users\radhe\Downloads`, which had these entries but the earlier extraction pass had not pulled them out):

- `C:\Users\radhe\PRISM_local_data\l4_mosaic\source_acquisitions_manifest.txt` (from `ch2_sar_ndxl_20250630my4rspwest_d_fp_xxx.zip`, internal path `miscellaneous/derived/20250630/ch2_sar_ndxl_20250630my4rspwest_d_fp_xxx.txt`)
- `C:\Users\radhe\PRISM_local_data\l3c_cpr\source_acquisitions_manifest.txt` (from `ch2_sar_ndxl_20250630mpcpspwest_d_fp_xxx.zip`, internal path `miscellaneous/derived/20250630/ch2_sar_ndxl_20250630mpcpspwest_d_fp_xxx.txt`)

Every line parsed successfully against the pattern `ch2_sar_ncxl_YYYYMMDDtHHMMSSFFF_d_fp_<station>` (602/602 matched, zero parse failures). Structured output: `outputs/objective1/dop/manifest_602_parsed.json`. Date range 2019-09-22 to 2023-10-18; station-code breakdown `d18`=367, `d32`=163, `n18`=47, `gds`=11, `g26`=9, `m65`=3, `mad`=2.

### 3. Number of acquisitions

602, identical between the Y4R and CPR mosaic manifests (set-compared this session, exact match, 0 in one but not the other).

### 4. Footprint method (as of the prior session)

Four methods were checked, in order of preference (cheapest / already-local first):

1. **Local metadata search** — searched the entire `PRISM` repo, `PRISM_local_data`, and the contents listing of every relevant zip in `Downloads` for any of the 602 manifest filenames, their timestamps, or any per-scene footprint/coverage index (KML, shapefile, coverage grid) bundled with the Y4R/CPR mosaic packages. Result: none found.
2. **PRADAN portal** (`pradan.issdc.gov.in`) — checked via `WebFetch`. Confirmed login requirement. No public/anonymous search, metadata query, or footprint API was found.
3. **Chandrayaan Data Explorer / map-based browse app** (`chmapbrowse.issdc.gov.in`) — checked via `WebFetch`. Same ISSDC login requirement; no public map/footprint query endpoint found.
4. **CH2DFSAR User Manual v1.0** (public PDF, no login) — defines processing levels but explicitly defers filename/naming-convention/footprint documentation to a separate "CH2DFSAR DPSIS" document, not itself linked from the manual and not located publicly in that session's search.

No method that avoids an authenticated ISSDC session was found at that time.

### 5–10 (prior session)

See the superseding sections above (§2–§9 of this updated document) for the current state of these items; the prior session's raw/calibrated ambiguity (its old §8) is resolved in §4 above. The prior session's rejection of the 2025-10-25 and 2025-11-06 raw products (its old §10) remains valid and unchanged — both are confirmed non-covering by real corner-coordinate geometry, in `docs/DOP_VALIDATION.md` and `outputs/objective1/dop/candidate_coverage_check.json`.
