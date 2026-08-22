# DOP_VALIDATION — Candidate-level DOP: BLOCKED at Phase E (candidate coverage)

**Date:** 2026-08-22

## Summary

Candidate-level DOP for `SP_840980_0797630` **could not be calculated** from the raw DFSAR product currently held in this repository, because that product's acquisition does not cover the candidate's location. This is a genuine, quantified geolocation blocker, not a formulation or calibration blocker. No DOP value is reported for the candidate. The existing 0.64 / 0.57 / 0.64 numbers from `notebooks/objective1_y4r_polarimetry.ipynb.ipynb` remain what they always were — diagnostics on an arbitrary, non-candidate 25×1024-pixel patch — and are **not** used, extended, or reinterpreted as the candidate's DOP here.

---

## 1. Raw product

`data/ch2_sar_nrxl_20251025t211236510_d_fp_d18/data/raw/20251025/ch2_sar_nrxl_20251025t211236510_d_r0a_xx_fp_xx_d18.dat` — L0A-RAW quad-pol, product_id `2575411`. See `docs/RAW_DFSAR_VALIDATION.md` for full metadata, binary structure, and polarization-mapping validation (Phases A-D, all completed).

## 2. Acquisition date

2025-10-25T21:12:36.616Z to 2025-10-25T21:14:03.719Z (≈87 s, orbit 27527, descending).

## 3. Candidate coordinate

`SP_840980_0797630`, lat **−84.098°**, lon **79.764°** (source: prior candidate-screening pipeline, `objective1_dfsar_validation.ipynb.ipynb`, reproduced today in `outputs/objective1/reproduction_log.json`).

## 4. Candidate image coordinates

**Not determined — blocked before this step.** See §6.

## 5. Window dimensions

**Not extracted — no window was cut.** Per task instruction, a candidate window was not fabricated when coverage could not be confirmed.

## 6. Coverage determination (Phase E) — BLOCKED HERE

**Method:** compared the candidate's lat/lon against the raw product's own `isda:Geometry_Parameters` block (4 corner lat/lons + scene center), taken directly from the `.dat` XML label. Distances computed via haversine great-circle distance on the sphere the product itself defines (`semi_major_radius = semi_minor_radius = 1,737,400 m`, `eccentricity = 0`, both from the same XML). Independently corroborated using the geometry CSV's satellite ephemeris (Lunar-Fixed-Frame position of the first record converted to sub-satellite lat/lon). Full numeric evidence and computation saved at `outputs/objective1/dop/candidate_coverage_check.json`.

| Reference point | Lat | Lon | Distance to candidate |
|---|---|---|---|
| Scene UL corner | −84.502295° | −23.217621° | 270.4 km |
| Scene UR corner | −84.556978° | −22.521599° | 267.9 km |
| Scene LR corner | −86.567711° | −77.521892° | 277.9 km |
| Scene LL corner | −86.482727° | −77.422285° | 280.3 km |
| **Scene center** | **−85.998683°** | **−43.600595°** | **265.7 km** |

Scene extent for context: ~135 km along-track (UL-LL / UR-LR edge length) × ~2.6 km cross-track (UL-UR / LL-LR edge length, consistent with the XML's `isda:swath = 4850 m` and the instrument's stated L-band footprint of 22.5-34 km at full illumination).

Independent corroboration: the geometry CSV's first ephemeris row places the sub-satellite point at lat −84.98°, lon **−6.34°** at acquisition start — consistent with the XML corner longitudes (−23° to −77°) and confirming the whole pass sweeps through longitudes far from the candidate's +79.764°.

**Geolocation method used:** whole-scene corner/center coordinates from the PDS4 label (no per-pixel geocoding grid exists in this product — see `docs/RAW_DFSAR_VALIDATION.md` §2/§8). **Uncertainty in this determination:** the corner coordinates are the product's own delivered geolocation and were not independently refined; however, the candidate is ~266-280 km outside the footprint while the scene itself is only ~135 km long — a margin roughly **2x the entire scene length**, and **>100x** the scene's cross-track width. No plausible geolocation error in a delivered PDS4 label (typically 10s of meters to a few km for this class of product) could close a 265+ km gap. The non-overlap conclusion is not sensitive to the exact precision of the corner coordinates.

```
BLOCKED AT: Candidate coverage (Phase E)
REASON: The only raw DFSAR L0A-RAW product present under PRISM/data (2025-10-25
        acquisition, orbit 27527, product_id 2575411) does not image the
        candidate's location. Its footprint is a ~135 km x 2.6 km strip
        centered near (-86.0 deg, -43.6 deg); the candidate sits at
        (-84.098 deg, +79.764 deg).
EVIDENCE: Haversine distance from the candidate to the nearest footprint
        reference point (scene center) is 265.7 km; to the nearest corner,
        267.9 km. Full computation in
        outputs/objective1/dop/candidate_coverage_check.json. Independently
        corroborated via the geometry CSV's satellite ephemeris (sub-satellite
        longitude ~-6 deg at acquisition start vs. candidate longitude +79.764 deg).
DISTANCE TO FOOTPRINT: ~265.7 km (to scene center) / ~267.9 km (to nearest corner).
DATA REQUIRED: A different raw DFSAR L0A-RAW (or higher-level full-polarimetric)
        acquisition whose footprint actually contains (-84.098 deg, +79.764 deg).
        Per task instruction, no search for or download of another copy of the
        current product, and no substitute product, was performed in this session.
```

## 7-15. Calibration, formulation, numerical results, validation, comparison, assumptions, limitations, scientific confidence

**Not performed.** Every one of these steps (Phases F-J) is downstream of and depends on a valid candidate window from Phase E. Producing any of them without real Phase E coverage would require fabricating a window, which is explicitly prohibited by the task brief. No numbers are reported for §7-15.

What **was** independently established, and remains valid infrastructure for whenever a covering product becomes available (see `docs/RAW_DFSAR_VALIDATION.md` for full detail):

- Binary structure of the raw product (offsets, line length, I/Q payload bounds) — **CONFIRMED**.
- Offset-binary sample decoding convention — **CONFIRMED**, empirically re-verified this session at a second file location.
- Polarization channel mapping G0→HV, G1→HH, G2→VV, G3→VH — HV/VH/VV **CONFIRMED**, HH **LIKELY** (correct group, weaker quantitative fit).
- A memory-safe, reusable `read_window()` reader (`src/dfsar_raw_reader.py`) implementing all of the above, ready to point at a covering product without re-deriving the byte structure.
- The mathematical formulation already present in `notebooks/objective1_y4r_polarimetry.ipynb.ipynb` (STEP 27-33: windowed 2×2 H/V covariance → linear-pol Stokes DOP `sqrt(S2²+S3²+S4²)/S1`) is a legitimate, textbook-standard construction (Stokes parameters from a spatial covariance/coherency estimate, not from single uncorrelated pixels — the notebook's own STEP 24 "naive" version was correctly self-flagged as invalid, since it degenerates to DOP≡1). This formulation, or the full quad-pol 4×4 covariance eigenvalue-purity variant (STEP 35), would be the candidates to apply **if and when** a covering raw product and a real candidate window exist. No formula was changed or invented in this session; none was run on fabricated data either.

## Explicitly not done, per the task's critical rules

- No DOP was fabricated, estimated, or assumed for the candidate.
- The prior 0.64 / 0.57 / 0.64 patch values were not reused, rescaled, or presented as the candidate's DOP.
- No candidate window was invented to force a result.
- No geolocation was invented — the coverage determination used only the product's own delivered metadata (XML corners + ephemeris CSV).
- No calibration constants were invented (moot — never reached).
- ML (Isolation Forest / CNN / classifiers) was not attempted, consistent with the task's scope limit and with there being no ground-truth ice labels.
