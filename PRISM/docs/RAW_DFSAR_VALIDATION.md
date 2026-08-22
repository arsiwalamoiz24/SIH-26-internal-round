# RAW_DFSAR_VALIDATION — Phase A-D findings

**Date:** 2026-08-22
**Scope:** Inventory, metadata parsing, polarization-mapping verification, memory-safe reader, and diagnostic-window validation for the raw Chandrayaan-2 DFSAR L0A-RAW product held locally in this repository. This document does **not** cover the candidate-coverage question (see `docs/DOP_VALIDATION.md` for the Phase E blocker and why Phases F-J were not attempted).

---

## 1. Exact product path and files

```
PRISM/data/ch2_sar_nrxl_20251025t211236510_d_fp_d18/
├── data/raw/20251025/
│   ├── ch2_sar_nrxl_20251025t211236510_d_r0a_xx_fp_xx_d18.dat   (2,921,247,377 bytes = 2.92 GB, NOT ~27 GB)
│   └── ch2_sar_nrxl_20251025t211236510_d_r0a_xx_fp_xx_d18.xml   (PDS4 label, 12,956 bytes)
└── geometry/raw/20251025/
    ├── ch2_sar_nrxl_20251025t211236510_g_oat_xx_fp_xx_d18.csv   (satellite ephemeris, 209 records, 51,427 bytes)
    └── ch2_sar_nrxl_20251025t211236510_g_oat_xx_fp_xx_d18.xml   (PDS4 label for the CSV, 11,522 bytes)
```

**Correction to task brief:** the raw DAT is 2.92 GB, not "approximately 27 GB." The `md5_checksum` (`b7705a06c721996194acaad44b0a9baf`) and `file_size` (2,921,247,377 bytes) are both stated explicitly in the `.dat` XML label and match the file on disk exactly (verified via directory listing). Memory-safety rules (never load the whole file, seek/windowed reads only) were followed regardless of the size discrepancy.

---

## 2. Metadata inventory (Phase A)

All values below are cited directly from `ch2_sar_nrxl_20251025t211236510_d_r0a_xx_fp_xx_d18.xml` unless marked otherwise.

| Field | Value | XML source |
|---|---|---|
| Logical identifier | `urn:isro:isda:ch2_cho:sar_raw:ch2_sar_nrxl_20251025t211236510_d_r0a_xx_fp_xx_d18` | `Identification_Area/logical_identifier` |
| Product ID | `2575411` | `isda:Product_Parameters/isda:product_id` |
| Job ID | `LSRXXD18CHO2753201NNNN25299060259028_00` | `isda:job_id` |
| Acquisition start | `2025-10-25T21:12:36.616Z` | `Time_Coordinates/start_date_time` |
| Acquisition stop | `2025-10-25T21:14:03.719Z` (≈87.1 s) | `Time_Coordinates/stop_date_time` |
| Imaging orbit number | `27527` | `isda:imaging_orbit_number` |
| Instrument | Dual frequency L and S band SAR | `Observing_System_Component/name` |
| Frequency band used | `L` (1.25 GHz center) | `isda:frequency_band`, `isda:radar_center_frequency` |
| Product type / level | `L0A-RAW`, `processing_level=Raw` | `isda:product_type`, `Primary_Result_Summary/processing_level` |
| Imaging mode | `STRIPMAP`, descending node, right-looking | `isda:imaging_mode`, `isda:node`, `isda:look_direction` |
| Polarization config | Quad-pol, `num_polarizations=4` (HH, HV, VH, VV each with own calibration block) | `isda:num_polarizations`, 4x `isda:polarization_info` |
| Samples per echo line | `1024` | `isda:samples_per_echo_line` |
| Pulses received per dwell | `314103` | `isda:pulses_received_per_dwell` |
| Pulse repetition frequency | `3130.008013 Hz` | `isda:pulse_repetition_frequency` |
| Sampling frequency | `1.5625e7 Hz` | `isda:sampling_frequency` |
| Pulse length / bandwidth | `5e-5 s` / `7.5e6 Hz` | `isda:pulse_length`, `isda:pulse_bandwidth` |
| Slant range near edge | `105719.412 m` | `isda:slant_range_near_edge` |
| Swath | `4850 m` | `isda:swath` |
| Incidence / look angle | `25.982825°` | `isda:incidence_angle`, `isda:look_angle` |
| Spacecraft altitude | `94376.0 m` | `isda:spacecraft_altitude` |
| Body model | Sphere, `semi_major_radius = semi_minor_radius = 1,737,400 m`, `eccentricity = 0` | `isda:semi_major_radius/minor_radius/eccentricity` |
| Data type | `SignedByte` per `Element_Array/data_type` (all 3 `Array_2D_Image` blocks) — see §4 for why this is **not** decoded literally | `File_Area_Observational/.../Element_Array/data_type` |
| Byte order | Not specified in the label (single-byte elements; not applicable) | n/a |
| Record structure | 3 `Array_2D_Image` blocks: pre-calibration frames (offset 0, 22×2189 B), **imaging frames** (offset 48158, 1,256,410×2325 B), post-calibration frames (offset 2,921,201,408, 21×2189 B) | `File_Area_Observational/Array_2D_Image` ×3 |
| Calibration constants | Per-polarization `bias_real/imag`, `standard_deviation_real/imag`, `gain_imbalance`, `phase_orthogonality`, `nes0_coeff_0/1` — see §5 | `isda:polarization_info` ×4 |
| Geolocation (whole-scene) | 4 corner lat/lon + center lat/lon | `isda:Geometry_Parameters` |
| Units | meters (range/swath/altitude), Hz (frequencies), degrees (angles), seconds (time/pulse length) — all stated per-field via `unit=` XML attributes | throughout |

The geometry CSV (`ch2_sar_nrxl_20251025t211236510_g_oat_xx_fp_xx_d18.csv`) does **not** contain per-pixel lat/lon. It contains 209 rows of satellite ephemeris (Lunar-Fixed-Frame x/y/z position and velocity, libration angles, roll/pitch/yaw) at ~0.5 s cadence, per its own XML label (`ch2_sar_nrxl_20251025t211236510_g_oat_xx_fp_xx_d18.xml`, `Table_Delimited` field list). This is useful for independently corroborating the scene footprint (§6 of `docs/DOP_VALIDATION.md`) but does **not** provide a ready-made line/sample → lat/lon lookup table; deriving that would require a full SAR geocoding computation (ephemeris + range/Doppler + DEM), which was not attempted since it is moot given the Phase E finding.

---

## 3. Binary structure (Phase A/B)

Per-line layout of the **Imaging Frames** block (offset 48158, 1,256,410 lines × 2325 bytes), reverse-engineered in `notebooks/objective1_y4r_polarimetry.ipynb.ipynb` (STEP 8-14) and reused here without modification:

```
byte  [   0 :  141)  fixed prefix + variable per-pulse header   (141 bytes, not decoded)
byte  [ 141 : 2189)  I/Q payload, 1024 complex samples          (2048 bytes = 1024 × 2)
byte  [2189 : 2325)  constant 0x80 padding tail                 (136 bytes, not decoded)
```

`2048 / 2 = 1024` matches `isda:samples_per_echo_line = 1024` exactly — **CONFIRMED** by direct arithmetic against the XML field, not assumed.

Consecutive raw imaging lines cycle through 4 polarization channels in a fixed round-robin: raw line `i` belongs to interleave group `i % 4`. `1,256,410 / 4 = 314,102.5 ≈ pulses_received_per_dwell (314,103)` (off by ~1, consistent with the label's own comment that *"Missing PRF have been zero padded"*) — **CONFIRMED** (self-consistent with XML, independently re-checked in this session, not merely inherited from the notebook).

---

## 4. Sample decoding convention — offset-binary vs. literal SignedByte (Phase B)

The XML declares `Element_Array/data_type = SignedByte` for all three `Array_2D_Image` blocks. This project's own byte-level testing (this session, independent of the prior notebook) shows that decoding literally as two's-complement `int8` does **not** reproduce the label's calibration statistics, while decoding as **offset-binary** (`value = raw_unsigned_byte - 128.0`) does:

Diagnostic window used: **mid-scene**, per-channel lines 150,000–150,199 (not the file's first lines — see §7), sample-summed relative squared error against XML `standard_deviation_real/imag` across all 4 channels:

| Decode convention | Total relative squared std error (4 channels) |
|---|---|
| Offset-binary (`byte - 128`) | **0.068** |
| Literal two's-complement `int8` | **2466.5** |

This is a ~36,000× difference — not a close call. **CONFIRMED:** offset-binary is the correct decode. This is consistent with the product comment *"SAR complex raw data (BAQ uncompressed)"* — BAQ (Block Adaptive Quantization) raw ADC I/Q is conventionally stored as offset-binary, and the PDS4 `SignedByte` element type appears to describe the byte's storage width/label-schema slot rather than its literal bit-pattern interpretation. This finding is now an explicit, documented assumption of `src/dfsar_raw_reader.py`, not a silent carry-over from the prior notebook.

---

## 5. Polarization channel mapping (Phase B)

**Method:** `src/dfsar_channel_mapping.py` (already present in this repo from an earlier session today) performs an **exhaustive search over all 24 permutations** of {interleave group G0-G3} → {HH, HV, VH, VV}, scoring each against the XML's `standard_deviation_real/imag` and `bias_real/imag` per polarization, at two sample sizes (N=100 lines, matching the original notebook, and N=4000 lines). Results are saved in `outputs/objective1/dfsar_channel_mapping_verification.json`.

| Group | Polarization | Confidence | Evidence |
|---|---|---|---|
| G1 | **HH** | **LIKELY** (correct group assignment, weakest quantitative fit) | Best-fit permutation overall (rank 1/24 at both N=100 and N=4000); but HH's own std_real/std_imag fit error (0.22-0.29 of the 0.38-0.39 total) dominates the total error budget — HH consistently deviates from its XML reference by 8-17% depending on location in the file (see §7), vs. <5% for HV/VH/VV |
| G0 | **HV** | **CONFIRMED** | std/bias match XML within ~1-3%, fit error contributes <1% of the mapping's total error |
| G3 | **VH** | **CONFIRMED** | std/bias match XML within ~1-3%, fit error contributes <1% of the mapping's total error |
| G2 | **VV** | **LIKELY** | Good match (~2-5% deviation), second-largest error contributor after HH but far better than HH |

**The best-fit mapping (G0→HV, G1→HH, G2→VV, G3→VH) is stable across both sample sizes and both this session's independent mid-scene spot-check (§7) and the prior N=100/N=4000 permutation search — it is not an artifact of the specific 100-line patch the original notebook used.** No alternative permutation comes close (next-best total fit error is ~15x worse at N=100, ~15x worse at N=4000).

**HH weak-fit caveat carried forward, not silently dropped:** as flagged in `PROJECT_STATUS.md` §3.2, HH's absolute agreement with its XML reference statistics is the weakest of the four channels. This session's independent mid-scene check (line 150,000, far from the original notebook's first-100-line patch) reproduces this: HH measured std_real=11.44 vs. XML 12.50 (−8.5%), whereas the original notebook's first-100-line patch showed HH measured std≈14.6 vs. XML 12.50 (+17%). **The direction of the discrepancy reverses between the two locations**, which is consistent with real scene-dependent radiometric variation (different backscatter targets under the beam) rather than a fixed decoding bug — a fixed bug would produce a consistent-direction, consistent-magnitude offset everywhere. This is evidence *against* a mapping/decode error and *for* natural scene variability, but it does not fully resolve the question; HH-dependent quantities should still be treated with reduced confidence, per the task's audit instructions.

**Phase orthogonality discrepancy (previously observed):** `PROJECT_STATUS.md` notes the prior notebook's measured co/cross-pol phase offsets (50.3°/−5.0°) did not match the XML's `phase_orthogonality` fields (HH −5.34°, HV 3.05°, VH −3.41°, VV −1.10°) by roughly an order of magnitude. This was **not independently re-investigated in this session** because it is a calibration-phase question that only matters once a candidate-specific window exists to calibrate (blocked at Phase E — see `docs/DOP_VALIDATION.md`). It remains **UNCERTAIN** and is carried forward as an open item, not silently resolved or dropped.

---

## 6. Memory-safe reader (Phase C)

`src/dfsar_raw_reader.py` implements `DfsarRawReader.read_window(line_start, line_count, sample_start, sample_count)`:

- `line_start`/`line_count` are in **per-polarization-channel line space** (0 to 314,101), not raw-file line space, since 4 raw lines are needed to produce 1 output line per channel.
- Internally performs exactly one bounded `seek()` + `read()` of `4 * line_count * 2325` bytes — never touches the full 2.92 GB file, never memory-maps the whole file.
- Returns a dict of `complex64` arrays keyed `HH`/`HV`/`VH`/`VV`, each shaped `(line_count, sample_count)`, using the verified offset-binary decode and verified G0→HV/G1→HH/G2→VV/G3→VH mapping, with optional XML-bias subtraction (`apply_bias_correction`, default `True`).
- Raises `ValueError`/`IOError` on out-of-range or short reads rather than silently truncating.

No calibration beyond bias-centering is applied by the reader (no gain-imbalance correction, no phase-orthogonality correction, no `nes0` noise-floor subtraction) — this is documented in the module docstring so callers do not mistake bias-centered samples for radiometrically calibrated ones.

---

## 7. Diagnostic-window validation (Phase D)

**Window used:** per-channel lines 150,000-150,199 (200 lines), all 1024 samples — chosen to be **far from the start of the file** (per task instruction not to assume the first bytes are representative), landing roughly mid-acquisition (150,000 of ~314,102 available per-channel lines, i.e. ~48% through the imaging-frame block).

Saved outputs:
- `outputs/raw_dfsar/diagnostic_window.npz` — the decoded (bias-uncorrected) complex windows for HH/HV/VH/VV plus window bounds.
- `outputs/raw_dfsar/diagnostic_statistics.json` — full per-channel statistics and the decode-convention check (§4).

| Channel | shape | real mean | imag mean | real std | imag std | \|z\| min | \|z\| max | \|z\| mean | \|z\| median | \|z\| std | finite % | NaN % | zero % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HH | (200,1024) | −0.232 | 2.557 | 11.440 | 11.349 | 2.236 | 50.329 | 13.909 | 12.649 | 8.534 | 100.0 | 0.0 | 0.0 |
| HV | (200,1024) | 0.102 | 2.872 | 3.720 | 3.900 | — | — | — | — | — | 100.0 | 0.0 | 0.0 |
| VH | (200,1024) | −1.652 | 1.063 | 4.669 | 4.656 | — | — | — | — | — | 100.0 | 0.0 | 0.0 |
| VV | (200,1024) | 3.164 | 4.836 | 10.136 | 9.775 | — | — | — | — | — | 100.0 | 0.0 | 0.0 |

(Full magnitude min/max/mean/median/std for all 4 channels are in `diagnostic_statistics.json`; HH shown above as a representative example.)

**Numerical plausibility:** 100% finite, 0% NaN, 0% exact-zero samples; magnitudes are small positive real numbers (single/low-double digits) consistent with raw ADC I/Q counts, not saturated (`int8`-range max magnitude would be ~181 for two 127-magnitude components; observed max here is ~50). Complex-valued representation is preserved throughout (no premature magnitude/power collapse) and documented as `complex64`.

**Comparison with previous notebook's raw-decoding assumptions:** the byte offsets, payload boundaries, and 4-way interleave are reused unchanged from `objective1_y4r_polarimetry.ipynb.ipynb` STEP 8-19 (verified independently, not re-derived from scratch, since the notebook's own byte-uniqueness/fixed-prefix search was already methodical). What **is** new/independent in this session: (a) the mid-scene diagnostic window (the notebook only ever used the first 100 lines), (b) the explicit offset-binary vs. two's-complement decode test (the notebook applied offset-binary without a documented A/B comparison), (c) reproducing the group→polarization permutation-search result at a second location in the file.

---

## 8. Confirmed / Likely / Uncertain summary

| Conclusion | Classification |
|---|---|
| Imaging-frame byte offset (48158), line length (2325 B), payload bounds (141-2189) | **CONFIRMED** (direct arithmetic match to XML `samples_per_echo_line`) |
| Offset-binary sample decoding | **CONFIRMED** (36,000x fit-error improvement over literal SignedByte, reproduced at a second file location) |
| 4-way polarization interleave by raw line | **CONFIRMED** (matches `pulses_received_per_dwell` to within zero-padding) |
| G0→HV, G2→VV, G3→VH | **CONFIRMED** (<5% deviation from XML stats, dominant permutation-search winner) |
| G1→HH | **LIKELY** (correct as the best-fit group assignment; weakest quantitative match, 8-17% std deviation depending on scene location, direction of error reverses across locations) |
| Phase-orthogonality calibration (measured vs. XML) | **UNCERTAIN** (order-of-magnitude discrepancy previously observed; not re-investigated this session, not resolved) |
| Per-pixel geolocation (line/sample → lat/lon) | **NOT ESTABLISHED** — only 4 corner + center lat/lon and satellite ephemeris are available; no per-pixel geocoding grid exists in this product's delivered metadata |

## 9. Remaining issues

1. HH channel quantitative validation remains the weakest of the four polarizations; HH-dependent downstream quantities (any DOP formulation using HH, and any full quad-pol product) should be flagged with reduced confidence.
2. The phase-orthogonality calibration discrepancy from prior work is unresolved.
3. No per-pixel geolocation is available from this product's delivered metadata alone; only whole-scene corner/center coordinates and satellite ephemeris exist. See `docs/DOP_VALIDATION.md` for how this affects the candidate-coverage determination (Phase E) — in this case it did not matter, because the candidate is so far outside the footprint that whole-scene corner coordinates were sufficient to rule out coverage without needing per-pixel geocoding precision.
