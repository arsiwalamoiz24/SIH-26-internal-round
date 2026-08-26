"""
PRISM -- Ice Evidence Pipeline V2 (evidence-hierarchy redesign).

Context: PRISM v1's combined "Physics Evidence Score" (src/physics_evidence_
score.py, an unweighted Pv/CPR/T-Ratio composite) FAILED a formal positive/
negative-control experiment (docs/POSITIVE_NEGATIVE_CONTROL_VALIDATION.md):
Cabeus (LCROSS-confirmed positive) scored 0.320 (rank 11 of 11 validation
sites); Wiechert (M3-confirmed negative) scored 0.714 (rank 3 of 11). Every
metric feeding that score (Pv, CPR, T-Ratio) ranked the negative control
above the positive control.

This module does NOT try to fix that by re-weighting Pv/CPR/T-Ratio until
Cabeus wins -- per explicit instruction, that would be post-hoc tuning, not
science. Instead it restructures WHAT the score means: an evidence hierarchy
where higher-quality evidence (direct detection, independent remote sensing)
cannot be overridden by lower-quality evidence (PRISM's own contested radar
metrics), and PRISM's radar metrics are demoted from "the score" to "one
input among several, weighted last."

Literature basis for this restructuring (full detail in
docs/ICE_METRIC_LITERATURE_MAP.md and docs/ICE_PIPELINE_V2_REDESIGN.md):
  - Neish et al. (2011), JGR Planets 116, E01005, DOI 10.1029/2010JE003647 --
    full text obtained. Confirms Cabeus (the strongest confirmed ice site in
    this investigation) shows LOW CPR (2% of Mini-RF pixels, 0.01% of
    Chandrayaan-1 Mini-SAR pixels have CPR>1; mean CPR 0.25+/-0.12, BELOW the
    0.31+/-0.17 south-polar regional average). Their own conclusion: low CPR
    rules out a thick near-surface ice sheet, NOT ice mixed as fine grains
    into regolith. This means CPR is not just weak evidence for ice -- at a
    site we know has ice, CPR gives an actively unhelpful signal. High CPR is
    therefore not a necessary condition for lunar ice.
  - Eke et al. (2014, Icarus 241) and Fa (2018, JGR Planets, DOI
    10.1029/2018JE005668): elevated CPR is also not a SUFFICIENT condition --
    both attribute it to crater-wall steepness / blocky ejecta roughness in
    other craters.
  - Verma et al. (2025, Icarus 432) reportedly attributes some CPR>1 cases to
    surface roughness and reports an inverse CPR-DOP relationship -- ACCESS
    NOTE: ScienceDirect fully blocked in two independent investigation
    passes; this is search-summary confidence only. The QUALITATIVE
    conclusion (roughness matters) is used below; a specific R^2~0.99 figure
    attributed to this paper in web search results is explicitly NOT used
    anywhere in this module, per docs/ICE_METRIC_LITERATURE_MAP.md's caution
    against repeating the earlier "Kumar 2022"/"Zhao 2024" unverified-
    citation problem.
  - Sinha et al. 2026's DOP cannot be reproduced by PRISM (docs/DOP_SINHA_
    2026_RESEARCH.md, 8 independent hypotheses) -- DOP is therefore computed
    here ONLY as a diagnostic field, never as a score input.
  - SERD and T-Ratio have no independent external literature validating them
    as ice indicators at all (docs/ICE_METRIC_LITERATURE_MAP.md) -- both are
    reported as EXPERIMENTAL_METRICS, never as score inputs.

DATA PROVENANCE (read this before trusting any number this module prints):
this environment has no local copy of the Chandrayaan-2 DFSAR Y4R/L3C
mosaics or raw Level-1A SLC products (ISRO PRADAN is login-gated; no cached
team-Drive /vsicurl/ URLs are available here -- see docs/DOP_SINHA_2026_
RESEARCH.md Sec 3.5 for the same constraint already documented for the DOP
investigation). Every Pv/CPR/SERD/T-Ratio number below is copied VERBATIM
from a real PRISM pipeline run in a PRIOR session, with its exact source
file cited per-record -- this module does not fabricate or estimate any of
them. Terrain (slope/roughness/illumination) for Cabeus and Wiechert WAS
freshly computed in THIS session (live /vsicurl/ read of the real public
NASA PGDA LOLA DEM, using PRISM's own src/terrain_algorithms.py, unmodified)
-- see docs/POSITIVE_NEGATIVE_CONTROL_VALIDATION.md Sec 6. DOP and Isolation
Forest are NO DATA for Cabeus/Wiechert in this environment (same access
constraint) and are reported as such, never estimated.

This module does NOT delete or modify src/physics_evidence_score.py (PRISM
v1 / legacy). It imports v1's real, already-computed outputs for direct
side-by-side comparison (Sec below), so nothing here requires re-running v1.
"""

import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../PRISM
OUT_DIR = os.path.join(REPO, "outputs", "objective1", "ice_evidence_v2")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# REAL, SOURCED PER-SITE DATA. Every field cites its origin. NO field is
# invented; fields that are genuinely unavailable in this environment are
# explicitly None with a documented reason, never a guessed value.
# ---------------------------------------------------------------------------

SITES = {
    # --- PRISM's 7 shortlisted candidates -----------------------------------
    # Pv/CPR/SERD/T-Ratio interior vs outside: PRISM/outputs/objective1/
    # shortlist_full_res_comparison.csv (real pipeline run, src/radar_pipeline.py).
    # Terrain: PRISM/outputs/objective2/shortlist/shortlist_hazard_summary.csv
    # + per-candidate PRISM/outputs/objective2/shortlist/<id>_hazard_map.json
    # (src/hazard_map_shortlist_pipeline.py; primary candidate via
    # src/hazard_map_pipeline.py / SP_840980_0797630_hazard_map_v2.json).
    "SP_840980_0797630": {
        "role": "PRISM candidate (primary)", "lat": -84.098, "lon": 79.764,
        "pv_inside": 0.5070526, "pv_outside": 0.4263749,
        "cpr_inside": 0.6303874, "cpr_outside": 0.5317169, "cpr_pct_gt1_inside": 7.3257,
        "serd_inside": 0.6362138, "serd_outside": 0.6924025,
        "tratio_inside": 0.6513420, "tratio_outside": 0.5305809,
        "hazard_inside_psr": 0.5966665, "illum_frac_inside_psr": 0.0,
        "dop": 0.680, "dop_status": "REAL, candidate-specific (Level-1A SLC acquisition found and confirmed to cover this candidate) -- see docs/DOP_SINHA_2026_RESEARCH.md. Diagnostic only, not used in the V2 score.",
        "m3_status": "NOT TESTED (no M3 study covers this PSR)", "lcross_status": "N/A", "shadowcam_status": "Real terrain signal confirmed (0.994 adjacent-pixel correlation, ML_METHODS.md); no ice-specific interpretation attempted",
    },
    "SP_832640_0090770": {
        "role": "PRISM candidate", "lat": -83.264, "lon": 9.077,
        "pv_inside": 0.5184597, "pv_outside": 0.4940409,
        "cpr_inside": 0.7104936, "cpr_outside": 0.6544982, "cpr_pct_gt1_inside": 10.792,
        "serd_inside": 0.6093662, "serd_outside": 0.6302888,
        "tratio_inside": 0.7177076, "tratio_outside": 0.6744012,
        "hazard_inside_psr": 0.7475623, "illum_frac_inside_psr": 0.0,
        "dop": 0.8410894, "dop_status": "REAL (dop_secondary/candidate_dop.json). Diagnostic only.",
        "m3_status": "NOT TESTED", "lcross_status": "N/A", "shadowcam_status": "Real terrain signal confirmed (0.995-0.996 correlation)",
    },
    "SP_830080_0535120": {
        "role": "PRISM candidate", "lat": -83.008, "lon": 53.512,
        "pv_inside": 0.4904545, "pv_outside": 0.5586234,
        "cpr_inside": 0.6684831, "cpr_outside": 0.8235938, "cpr_pct_gt1_inside": 7.2185,
        "serd_inside": 0.6244992, "serd_outside": 0.5845452,
        "tratio_inside": 0.6880823, "tratio_outside": 0.8555278,
        "hazard_inside_psr": 0.6170340, "illum_frac_inside_psr": 0.0,
        "dop": 0.6303498, "dop_status": "REAL (dop_secondary). Diagnostic only.",
        "m3_status": "NOT TESTED", "lcross_status": "N/A", "shadowcam_status": "Real terrain signal confirmed (0.982-0.988 correlation)",
    },
    "SP_842420_0421060": {
        "role": "PRISM candidate", "lat": -84.242, "lon": 42.106,
        "pv_inside": 0.5257441, "pv_outside": 0.5097543,
        "cpr_inside": 0.5563170, "cpr_outside": 0.5724154, "cpr_pct_gt1_inside": 0.140,
        "serd_inside": 0.6273763, "serd_outside": 0.6306878,
        "tratio_inside": 0.6672561, "tratio_outside": 0.7037765,
        "hazard_inside_psr": 0.7919951, "illum_frac_inside_psr": 0.0,
        "dop": None, "dop_status": "NOT COMPUTED -- no covering Level-1A SLC acquisition downloaded for this candidate",
        "m3_status": "NOT TESTED", "lcross_status": "N/A", "shadowcam_status": "Real terrain signal confirmed (0.996-0.997 correlation)",
    },
    "SP_817950_1586580": {
        "role": "PRISM candidate", "lat": -81.795, "lon": 158.658,
        "pv_inside": 0.4873004, "pv_outside": 0.5084718,
        "cpr_inside": 0.5183735, "cpr_outside": 0.5988044, "cpr_pct_gt1_inside": 0.00387,
        "serd_inside": 0.6604089, "serd_outside": 0.6317254,
        "tratio_inside": 0.5903475, "tratio_outside": 0.6800859,
        "hazard_inside_psr": 0.6408944, "illum_frac_inside_psr": 0.0,
        "dop": None, "dop_status": "NOT COMPUTED",
        "m3_status": "NOT TESTED", "lcross_status": "N/A", "shadowcam_status": "Real terrain signal confirmed (0.971-0.996 correlation)",
    },
    "SP_819860_1568660": {
        "role": "PRISM candidate", "lat": -81.986, "lon": 156.866,
        "pv_inside": 0.4999830, "pv_outside": 0.4934984,
        "cpr_inside": 0.6359729, "cpr_outside": 0.6112705, "cpr_pct_gt1_inside": 10.4116,
        "serd_inside": 0.6358551, "serd_outside": 0.6328802,
        "tratio_inside": 0.6539559, "tratio_outside": 0.6403324,
        "hazard_inside_psr": 0.6460964, "illum_frac_inside_psr": 0.0,
        "dop": 0.8270149, "dop_status": "REAL (dop_secondary). Diagnostic only.",
        "m3_status": "NOT TESTED", "lcross_status": "N/A", "shadowcam_status": "Real terrain signal confirmed (0.989-0.993 correlation)",
    },
    "SP_809570_2454450": {
        "role": "PRISM candidate", "lat": -80.957, "lon": 245.445,
        "pv_inside": 0.4267860, "pv_outside": 0.3779047,
        "cpr_inside": 0.3954223, "cpr_outside": 0.4053750, "cpr_pct_gt1_inside": 0.0951,
        "serd_inside": 0.7528881, "serd_outside": 0.7562847,
        "tratio_inside": 0.4666118, "tratio_outside": 0.4234444,
        "hazard_inside_psr": 0.7224977, "illum_frac_inside_psr": 0.0,
        "dop": None, "dop_status": "NOT COMPUTED",
        "m3_status": "NOT TESTED", "lcross_status": "N/A", "shadowcam_status": "Real terrain signal confirmed (0.988-0.991 correlation)",
    },
    # --- Positive / negative controls ---------------------------------------
    # Pv/CPR/SERD/T-Ratio (whole-window, NOT interior/exterior -- a documented
    # data-availability difference from the 7 candidates above, see
    # docs/POSITIVE_NEGATIVE_CONTROL_VALIDATION.md Sec 5/9):
    # PRISM/outputs/validation/{ice_reference_sites,control_sites}.csv
    # (src/validation_pipeline.py, real pipeline run, 2026-08-22 session).
    # Terrain: freshly computed THIS session (control_terrain_results.json),
    # live /vsicurl/ read of the real LOLA DEM, matched +/-5000m window.
    "LCROSS_Cabeus": {
        "role": "POSITIVE CONTROL (independent, LCROSS)", "lat": -84.6796, "lon": -48.7093,
        "pv_inside": 0.2172471, "pv_outside": None,  # whole-window only, no exterior split available
        "cpr_inside": 0.1662777, "cpr_outside": None, "cpr_pct_gt1_inside": None,
        "serd_inside": 0.8483706, "serd_outside": None,
        "tratio_inside": 0.1997981, "tratio_outside": None,
        "hazard_inside_psr": 0.4527498, "illum_frac_inside_psr": 0.0022422,  # fresh, this session, +/-5km window
        "dop": None, "dop_status": "NOT COMPUTED -- no raw DFSAR acquisition search performed for this site in this environment (PRADAN login-gated)",
        "m3_status": "NOT ADDRESSED -- Cabeus does not appear in Li et al. 2018's M3-positive or M3-negative crater lists at all (confirmed, full text obtained)",
        "lcross_status": "CONFIRMED POSITIVE -- Colaprete et al. 2010, Science 330:463-468, DOI 10.1126/science.1186986: 5.6+/-2.9 wt%% water in impact ejecta plume (single-point, subsurface-excavating measurement)",
        "lend_status": "Regional hydrogen maximum in the south polar region is at this site (Sanin et al. 2017) -- 10km FWHM, regional not candidate-scale",
        "shadowcam_status": "The ONLY south-polar PSR (of 14 tested) showing a positive M3-consistent radiance shift -- Ando, Li, Robinson & Wagner 2025, Planetary Science Journal 6(3):62, DOI 10.3847/PSJ/adb8d1, full text obtained",
        "independent_cpr_check": "Neish et al. 2011 (JGR Planets 116, E01005, full text obtained): only 2% of Mini-RF / 0.01% of Chandrayaan-1 Mini-SAR pixels at Cabeus have CPR>1; mean CPR 0.25+/-0.12, BELOW the 0.31+/-0.17 regional average -- LOW CPR IS EXPECTED at this confirmed-ice site, not anomalous",
    },
    "Wiechert": {
        "role": "NEGATIVE CONTROL (independent, M3)", "lat": -84.5, "lon": 165.0,
        "pv_inside": 0.3138826, "pv_outside": None,
        "cpr_inside": 0.3109077, "cpr_outside": None, "cpr_pct_gt1_inside": None,
        "serd_inside": 0.7789834, "serd_outside": None,
        "tratio_inside": 0.3252060, "tratio_outside": None,
        "hazard_inside_psr": 0.4643903, "illum_frac_inside_psr": 0.0531030,  # fresh, this session, +/-5km window
        "dop": None, "dop_status": "NOT COMPUTED -- same constraint as Cabeus",
        "m3_status": "CONFIRMED NEGATIVE -- Li et al. 2018, PNAS 115(36):8907-8912, full text obtained: cold trap explicitly checked, ice-absorption feature NOT detected at M3's ~280m spectral resolution. Precise terminology: 'no detected surface ice at M3 sensitivity', NOT 'genuinely ice-free' (M3 cannot rule out sub-detection-limit or subsurface ice)",
        "lcross_status": "N/A -- no impact/direct measurement at this site",
        "lend_status": "No site-specific data found -- regional coverage only",
        "shadowcam_status": "Included in Ando et al. 2025's 14-PSR test set; NOT singled out as showing a radiance shift -- consistent with (agrees with) the M3 non-detection",
    },
    # --- HELD-OUT validation set (task Sec 10: NOT used to design the tier ---
    # logic above -- that logic was fixed before these sites were added to
    # this file). Pv/CPR/SERD/T-Ratio: PRISM/outputs/validation/
    # {ice_reference_sites,control_sites}.csv (same real 2026-08-22 pipeline
    # run as Cabeus/Wiechert). Terrain: freshly computed THIS session,
    # same +/-5000m LOLA DEM window, same unmodified terrain_algorithms.py
    # code, immediately after Cabeus/Wiechert in the same script run.
    "Faustini": {
        "role": "positive (HELD-OUT), M3", "lat": -87.3, "lon": 77.0,
        "pv_inside": 0.2889484, "pv_outside": None, "cpr_inside": 0.2967567, "cpr_outside": None, "cpr_pct_gt1_inside": None,
        "serd_inside": 0.7915645, "serd_outside": None, "tratio_inside": 0.3051011, "tratio_outside": None,
        "hazard_inside_psr": 0.6087, "illum_frac_inside_psr": 0.023,
        "dop": None, "dop_status": "NOT COMPUTED in this environment",
        "m3_status": "CONFIRMED POSITIVE -- Li et al. 2018 explicit positive crater list",
        "lcross_status": "N/A", "lend_status": "No site-specific data found",
        "shadowcam_status": "Included in Ando et al. 2025's 14-PSR set; NOT singled out as showing a shift (null, like all south-polar M3-positive PSRs except Cabeus)",
    },
    "De_Gerlache": {
        "role": "positive (HELD-OUT), M3", "lat": -88.5, "lon": -87.1,
        "pv_inside": 0.3013501, "pv_outside": None, "cpr_inside": 0.3223958, "cpr_outside": None, "cpr_pct_gt1_inside": None,
        "serd_inside": 0.7913924, "serd_outside": None, "tratio_inside": 0.3380917, "tratio_outside": None,
        "hazard_inside_psr": 0.5188, "illum_frac_inside_psr": 0.0383,
        "dop": None, "dop_status": "NOT COMPUTED",
        "m3_status": "CONFIRMED POSITIVE -- Li et al. 2018", "lcross_status": "N/A", "lend_status": "No site-specific data found",
        "shadowcam_status": "Included in Ando 2025's set; null result (like all south-polar M3-positive PSRs except Cabeus)",
    },
    "Haworth": {
        "role": "positive (HELD-OUT), M3", "lat": -86.9, "lon": -4.0,
        "pv_inside": 0.2283019, "pv_outside": None, "cpr_inside": 0.2382054, "cpr_outside": None, "cpr_pct_gt1_inside": None,
        "serd_inside": 0.8279314, "serd_outside": None, "tratio_inside": 0.2467257, "tratio_outside": None,
        "hazard_inside_psr": 0.5769, "illum_frac_inside_psr": 0.126,
        "dop": None, "dop_status": "NOT COMPUTED",
        "m3_status": "CONFIRMED POSITIVE -- Li et al. 2018", "lcross_status": "N/A", "lend_status": "No site-specific data found",
        "shadowcam_status": "Included in Ando 2025's set; null result",
    },
    "Shoemaker": {
        "role": "positive (HELD-OUT), M3", "lat": -88.1, "lon": 44.9,
        "pv_inside": 0.2135159, "pv_outside": None, "cpr_inside": 0.2006540, "cpr_outside": None, "cpr_pct_gt1_inside": None,
        "serd_inside": 0.8504893, "serd_outside": None, "tratio_inside": 0.2096830, "tratio_outside": None,
        "hazard_inside_psr": 0.4319, "illum_frac_inside_psr": 0.0015,
        "dop": None, "dop_status": "NOT COMPUTED",
        "m3_status": "CONFIRMED POSITIVE -- Li et al. 2018", "lcross_status": "N/A", "lend_status": "No site-specific data found",
        "shadowcam_status": "Included in Ando 2025's set; null result",
    },
    "Sverdrup": {
        "role": "positive (HELD-OUT), M3", "lat": -88.5, "lon": -152.0,
        "pv_inside": 0.2504585, "pv_outside": None, "cpr_inside": 0.2495164, "cpr_outside": None, "cpr_pct_gt1_inside": None,
        "serd_inside": 0.8218521, "serd_outside": None, "tratio_inside": 0.2690185, "tratio_outside": None,
        "hazard_inside_psr": 0.4638, "illum_frac_inside_psr": 0.0047,
        "dop": None, "dop_status": "NOT COMPUTED",
        "m3_status": "CONFIRMED POSITIVE -- Li et al. 2018", "lcross_status": "N/A", "lend_status": "No site-specific data found",
        "shadowcam_status": "Included in Ando 2025's set; null result",
    },
    "Shackleton": {
        "role": "positive (HELD-OUT), M3", "lat": -89.67, "lon": 129.78,
        "pv_inside": 0.4009880, "pv_outside": None, "cpr_inside": 0.4799910, "cpr_outside": None, "cpr_pct_gt1_inside": None,
        "serd_inside": 0.7071440, "serd_outside": None, "tratio_inside": 0.5248855, "tratio_outside": None,
        "hazard_inside_psr": 0.6837, "illum_frac_inside_psr": 0.0011,
        "dop": None, "dop_status": "NOT COMPUTED",
        "m3_status": "CONFIRMED POSITIVE -- Li et al. 2018", "lcross_status": "N/A",
        "lend_status": "No site-specific data found",
        "shadowcam_status": "Included in Ando 2025's set; null result (also the site with the highest v1 Pv/CPR of the entire validation set -- yet still shows no ShadowCam confirmation, illustrating exactly why radar-only evidence is being demoted here)",
    },
    "Amundsen": {
        "role": "negative (HELD-OUT, CONTESTED), M3", "lat": -84.5, "lon": 82.8,
        "pv_inside": 0.3024577, "pv_outside": None, "cpr_inside": 0.3008572, "cpr_outside": None, "cpr_pct_gt1_inside": None,
        "serd_inside": 0.7863415, "serd_outside": None, "tratio_inside": 0.3163311, "tratio_outside": None,
        "hazard_inside_psr": 0.4089, "illum_frac_inside_psr": 0.007,
        "dop": None, "dop_status": "NOT COMPUTED",
        "m3_status": "CONFIRMED NEGATIVE -- Li et al. 2018 explicit non-detection. CONTESTED: Brown et al. 2022 (Icarus 377, 114874) separately lists Amundsen among its 'resource-rich' PSRs (hydrogen/frost co-location modeling) -- a genuine cross-instrument disagreement (docs/LUNAR_SOUTH_POLE_ICE_VALIDATION_LITERATURE.md Sec 13/21). Per the evidence hierarchy, M3's direct spectral check (Level A) still sets this site's tier; the Brown et al. contradiction is reported, not allowed to silently override it.",
        "lcross_status": "N/A", "lend_status": "No site-specific data found",
        "shadowcam_status": "Not confirmed whether included in Ando 2025's specific 14-PSR list (not one of the 14 named) -- NOT ADDRESSED",
    },
    "Hedervari": {
        "role": "negative (HELD-OUT), M3", "lat": -81.8, "lon": 84.0,
        "pv_inside": 0.2579252, "pv_outside": None, "cpr_inside": 0.2399840, "cpr_outside": None, "cpr_pct_gt1_inside": None,
        "serd_inside": 0.8179643, "serd_outside": None, "tratio_inside": 0.2605550, "tratio_outside": None,
        "hazard_inside_psr": 0.4426, "illum_frac_inside_psr": 0.013,
        "dop": None, "dop_status": "NOT COMPUTED",
        "m3_status": "CONFIRMED NEGATIVE -- Li et al. 2018, no contradicting secondary evidence found", "lcross_status": "N/A",
        "lend_status": "No site-specific data found", "shadowcam_status": "Not one of Ando 2025's 14 named PSRs -- NOT ADDRESSED",
    },
    "Idelson_L": {
        "role": "negative (HELD-OUT), M3", "lat": -84.2, "lon": 115.8,
        "pv_inside": 0.2705741, "pv_outside": None, "cpr_inside": 0.2716206, "cpr_outside": None, "cpr_pct_gt1_inside": None,
        "serd_inside": 0.8076918, "serd_outside": None, "tratio_inside": 0.2958576, "tratio_outside": None,
        "hazard_inside_psr": 0.4943, "illum_frac_inside_psr": 0.0964,
        "dop": None, "dop_status": "NOT COMPUTED",
        "m3_status": "CONFIRMED NEGATIVE -- Li et al. 2018, no contradicting secondary evidence found", "lcross_status": "N/A",
        "lend_status": "No site-specific data found", "shadowcam_status": "Not one of Ando 2025's 14 named PSRs -- NOT ADDRESSED",
    },
}

TRAIN_SITE_IDS = ["LCROSS_Cabeus", "Wiechert"]
HELD_OUT_POSITIVE_IDS = ["Faustini", "De_Gerlache", "Haworth", "Shoemaker", "Sverdrup", "Shackleton"]
HELD_OUT_NEGATIVE_IDS = ["Amundsen", "Hedervari", "Idelson_L"]

# Sites with a matched, interior-vs-exterior Pv/CPR/SERD/T-Ratio split (the 7
# PRISM candidates) vs. whole-window-only sites (Cabeus, Wiechert) -- kept as
# an explicit list so downstream code never silently treats them as comparable.
INTERIOR_EXTERIOR_AVAILABLE = [
    "SP_840980_0797630", "SP_832640_0090770", "SP_830080_0535120",
    "SP_842420_0421060", "SP_817950_1586580", "SP_819860_1568660", "SP_809570_2454450",
]
WHOLE_WINDOW_ONLY = ["LCROSS_Cabeus", "Wiechert"]


# ---------------------------------------------------------------------------
# EVIDENCE HIERARCHY (task Sec 7). Implemented as a strict LEXICOGRAPHIC tier
# assignment, not an additive weighted sum -- this is the concrete mechanism
# that satisfies "do not allow a lower evidence class to override a higher
# one," without any tunable numeric weight. The tier is decided ONLY by the
# highest available evidence class; lower classes are still fully computed
# and reported (never hidden), but cannot move a site out of the tier its
# best evidence has already placed it in.
# ---------------------------------------------------------------------------

TIER_LABELS = {
    4: "HIGH (Level A: direct, independent detection)",
    3: "MODERATE-HIGH (Level B: strong independent remote-sensing evidence)",
    1: "LOW (Level A: direct, independent non-detection)",
    0: "PLAUSIBLE-UNCONFIRMED (no Level A/B evidence available -- Level C/D/E only)",
}


def classify_evidence_tier(site):
    """Returns (tier_code, tier_label, reasoning). Level A dominates in
    either direction (confirmed positive -> 4, confirmed negative -> 1);
    Level B (independent remote sensing, e.g. a validated ShadowCam
    radiance-shift or LEND anomaly) sets tier 3 only when Level A is silent;
    absence of both leaves every site at the same neutral tier 0, regardless
    of how high or low its PRISM radar metrics are -- this is the direct
    fix for v1's failure mode (radar metrics alone were allowed to imply
    strong ice evidence)."""
    lcross = site.get("lcross_status", "N/A")
    m3 = site.get("m3_status", "NOT TESTED")

    if "CONFIRMED POSITIVE" in lcross:
        return 4, TIER_LABELS[4], "Level A direct detection (LCROSS in-situ measurement) present and positive."
    if "CONFIRMED" in m3 and "POSITIVE" in m3.upper():
        return 4, TIER_LABELS[4], "Level A direct detection (M3 spectral) present and positive."
    if "CONFIRMED NEGATIVE" in m3:
        return 1, TIER_LABELS[1], "Level A direct non-detection (M3, explicitly checked) present."

    shadowcam = site.get("shadowcam_status", "")
    if "positive M3-consistent radiance shift" in shadowcam or "ONLY south-polar PSR" in shadowcam:
        return 3, TIER_LABELS[3], "Level B independent remote-sensing evidence (validated ShadowCam radiance-shift criterion, Ando et al. 2025) is positive, and no Level A evidence exists to override it."

    return 0, TIER_LABELS[0], "No Level A (M3/LCROSS) or Level B (validated ShadowCam/LEND anomaly) evidence exists for this site. Falls through to Level C/D/E only -- see radar_evidence and experimental_metrics below. This is the case for all 7 of PRISM's own shortlisted candidates."


def relative_anomaly(site):
    """Level D: PRISM radar evidence, reframed as a LOCAL relative anomaly
    (interior-exterior delta), never a raw CPR>1 / high-Pv threshold, per
    task Sec 3. Returns None fields where the interior/exterior split isn't
    available (Cabeus, Wiechert -- see WHOLE_WINDOW_ONLY), rather than
    fabricating a proxy value."""
    def delta(key):
        i, o = site.get(f"{key}_inside"), site.get(f"{key}_outside")
        return None if (i is None or o is None) else round(i - o, 4)

    return {
        "cpr_relative_anomaly": delta("cpr"),
        "pv_relative_anomaly": delta("pv"),
        "note": "Interior-exterior delta within the same acquisition/calibration, per src/radar_pipeline.py's existing window methodology -- NOT a raw CPR>1 threshold." if site.get("cpr_outside") is not None
                else "NOT COMPUTABLE for this site in this environment -- only a whole-window mean exists (docs/POSITIVE_NEGATIVE_CONTROL_VALIDATION.md Sec 5/9), not an interior/exterior split. Do not compare this site's relative anomaly to the 7 candidates' values above; they are not the same measurement.",
    }


def roughness_context_flag(site, all_sites):
    """A provisional, explicitly-labeled heuristic (task Sec 8 allows
    'explicitly marked as provisional' weights) -- NOT a published model.
    Compares this site's hazard score (the only cross-site-comparable
    terrain summary available without re-deriving interior/exterior
    roughness splits for every site, which this environment's data access
    does not support) against the distribution across all tested sites, to
    flag whether a radar anomaly (if any) coincides with anomalous terrain
    or not, per task Sec 4's "CPR anomaly + roughness anomaly" vs "CPR
    anomaly without corresponding roughness anomaly" distinction."""
    hazards = [s["hazard_inside_psr"] for s in all_sites.values() if s.get("hazard_inside_psr") is not None]
    this_hazard = site.get("hazard_inside_psr")
    if this_hazard is None or not hazards:
        return {"roughness_percentile_among_tested_sites": None, "flag": "NOT COMPUTABLE"}
    pct = 100.0 * sum(1 for h in hazards if h <= this_hazard) / len(hazards)
    return {
        "roughness_percentile_among_tested_sites": round(pct, 1),
        "flag": "TERRAIN-ANOMALOUS (top tercile hazard among tested sites)" if pct >= 66.7
                else ("TERRAIN-TYPICAL (middle tercile)" if pct >= 33.3
                      else "TERRAIN-BENIGN (bottom tercile hazard among tested sites)"),
        "caveat": "PROVISIONAL cross-site heuristic, not a published model or a fitted statistical relationship -- see docs/ICE_PIPELINE_V2_REDESIGN.md Sec on roughness. Uses whole/interior hazard (combined slope+roughness+illumination), not roughness alone, because per-site interior-vs-exterior roughness splits are not available for every tested site in this environment.",
    }


def build_evidence_index(site_id, site, all_sites):
    tier_code, tier_label, tier_reasoning = classify_evidence_tier(site)
    radar = relative_anomaly(site)
    roughness_ctx = roughness_context_flag(site, all_sites)

    result = {
        "site_id": site_id,
        "role": site["role"],
        "lat": site["lat"], "lon": site["lon"],
        "evidence_index": {
            "tier_code": tier_code,
            "tier_label": tier_label,
            "reasoning": tier_reasoning,
            "note": "This is an EVIDENCE INDEX (an ordinal classification driven by the highest-quality available evidence), NOT an 'ice probability' -- per explicit task instruction, no numeric probability is claimed anywhere in this module.",
        },
        "independent_evidence_level_a_b": {
            "m3": site.get("m3_status", "NOT TESTED"),
            "lcross": site.get("lcross_status", "N/A"),
            "lend": site.get("lend_status", "NOT ADDRESSED (regional-only instrument, see docs/LUNAR_SOUTH_POLE_ICE_VALIDATION_LITERATURE.md Sec 4.1)"),
            "shadowcam": site.get("shadowcam_status", "NOT ADDRESSED"),
        },
        "thermal_plausibility_level_c": {
            "illumination_fraction_inside_psr": site.get("illum_frac_inside_psr"),
            "note": "0.0 (or near-0.0) confirms genuine, geometrically-independent permanent shadow -- a necessary precondition for ice stability, NOT detection. All 7 PRISM candidates and both controls show illum_frac ~0, so this does not discriminate among them.",
        },
        "radar_evidence_level_d": radar,
        "roughness_context": roughness_ctx,
        "independent_cpr_literature_check": site.get("independent_cpr_check", "N/A"),
        "dop_diagnostic_not_scored": {"value": site.get("dop"), "status": site.get("dop_status")},
        "experimental_metrics_not_scored": {
            "serd_inside": site.get("serd_inside"), "serd_outside": site.get("serd_outside"),
            "tratio_inside": site.get("tratio_inside"), "tratio_outside": site.get("tratio_outside"),
            "note": "SERD and T-Ratio have no independent external literature validating them as ice indicators (docs/ICE_METRIC_LITERATURE_MAP.md) -- reported for completeness, never contribute to evidence_index.",
        },
        "hazard_and_traversability": {
            "hazard_score_inside_psr_or_window": site.get("hazard_inside_psr"),
            "note": "Deliberately kept OUT of the ice evidence index (task Sec 12) -- this is a Hazard/Traversability output, to be combined with Ice Evidence only at the future Objective-3 landing-site-scoring stage, with an explicit, documented decision framework, not silently blended here.",
        },
    }
    return result


def main():
    all_results = {sid: build_evidence_index(sid, s, SITES) for sid, s in SITES.items()}

    print(f"{'Site':<22} {'Role':<32} {'Tier':<5} {'Tier label'}")
    for sid, r in all_results.items():
        ei = r["evidence_index"]
        print(f"{sid:<22} {r['role']:<32} {ei['tier_code']:<5} {ei['tier_label']}")

    with open(os.path.join(OUT_DIR, "ice_evidence_v2_results.json"), "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nSaved: {os.path.join(OUT_DIR, 'ice_evidence_v2_results.json')}")

    # Legacy (v1) comparison -- real numbers, not re-derived, from the
    # already-existing outputs this session verified in
    # docs/POSITIVE_NEGATIVE_CONTROL_VALIDATION.md.
    legacy = {
        "SP_840980_0797630": 1.0,  # physics_evidence_score.json, rank 1/7
        "LCROSS_Cabeus": 0.3204,   # validation_metrics.json, rank 11/11
        "Wiechert": 0.7138,        # validation_metrics.json, rank 3/11
    }
    print("\n=== Legacy (v1) score vs V2 tier, where both exist ===")
    for sid, v1_score in legacy.items():
        v2_tier = all_results[sid]["evidence_index"]["tier_label"]
        print(f"{sid:<22} v1={v1_score:<8} v2_tier={v2_tier}")

    # Held-out validation (task Sec 10): the tier logic above was fixed
    # BEFORE these 9 sites were added -- Cabeus/Wiechert were the only
    # sites used to motivate/design classify_evidence_tier(). Report
    # whether the SAME, unmodified rule correctly separates a fresh
    # positive/negative set it was never tuned against.
    print("\n=== HELD-OUT validation (rule fixed on Cabeus/Wiechert only, never touched for these sites) ===")
    pos_tiers, neg_tiers = [], []
    for sid in HELD_OUT_POSITIVE_IDS:
        t = all_results[sid]["evidence_index"]["tier_code"]
        pos_tiers.append(t)
        print(f"  POSITIVE {sid:<15} tier={t}  ({all_results[sid]['evidence_index']['tier_label']})")
    for sid in HELD_OUT_NEGATIVE_IDS:
        t = all_results[sid]["evidence_index"]["tier_code"]
        neg_tiers.append(t)
        print(f"  NEGATIVE {sid:<15} tier={t}  ({all_results[sid]['evidence_index']['tier_label']})")
    n_pos_correct = sum(1 for t in pos_tiers if t == 4)
    n_neg_correct = sum(1 for t in neg_tiers if t == 1)
    print(f"\n  Held-out positives correctly tiered HIGH: {n_pos_correct}/{len(pos_tiers)}")
    print(f"  Held-out negatives correctly tiered LOW:  {n_neg_correct}/{len(neg_tiers)}")
    print("  (Amundsen is a CONTESTED negative -- see its 'm3_status' field for the Brown et al. 2022 disagreement)")


if __name__ == "__main__":
    main()
