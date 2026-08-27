"""
PRISM -- Ice Radar Characterization V3.

Scientific question: "Can PRISM distinguish ice-related radar behavior from
roughness-related radar behavior?" This module does NOT produce an ice
score (see src/ice_evidence_pipeline_v2.py for the evidence-hierarchy
score, UNMODIFIED by this file). It produces a RADAR CHARACTERIZATION
VECTOR per site, with every quantity labeled either as a real, directly-
computed value or as NO DATA -- never estimated, never tuned to make any
site "pass."

Read docs/DFSAR_POLARIMETRIC_CHANNEL_AUDIT.md before trusting any number
here -- it establishes, per product type, what PRISM's bands actually are
and which quantities are genuinely self-computed from raw channels versus
read as ISRO-precomputed derived bands.

FOUNDATIONAL LITERATURE (verified this session, full citations in
docs/ICE_RADAR_V3_REDESIGN.md):
  - Neish et al. (2011), JGR Planets 116, E01005, DOI 10.1029/2010JE003647:
    Cabeus (LCROSS-confirmed water) has LOW CPR (2% of Mini-RF pixels,
    0.01% of Chandrayaan-1 Mini-SAR pixels have CPR>1; mean 0.25+/-0.12,
    below the 0.31+/-0.17 regional average). Provides the Stokes CPR
    formulation implemented here: CPR = (S1-S4)/(S1+S4).
  - Carter et al. (2012), JGR Planets 117, E00H09, DOI 10.1029/2011JE003911
    (CONFIRMED this session, full text, verbatim quotes in the redesign
    doc): CPR is driven by wavelength-scale roughness AND double-bounce
    geometry -- both non-ice-specific mechanisms.
  - Eke et al. (2014, Icarus 241) / Fa (2018, JGR Planets, DOI
    10.1029/2018JE005668): elevated CPR at various craters attributed to
    wall steepness / blocky ejecta, not ice.
  - Li et al. (2018), PNAS: M3 direct spectral ice evidence, full text.
  - Colaprete et al. (2010), Science: LCROSS direct water detection.
  - Sinha et al. 2026: DOP/CPR DFSAR criterion -- NOT reproduced by PRISM
    (docs/DOP_SINHA_2026_RESEARCH.md). Sinha's 0.13 DOP threshold is NOT
    hard-coded anywhere in this module.
  - Verma et al. 2025: ScienceDirect remains fully inaccessible (confirmed
    again this session). Only the qualitative "roughness matters, CPR/DOP
    anti-correlate" conclusion is referenced; no specific unverified number
    (e.g. an R^2 figure) from it is used anywhere in this file.

DATA REALITY (see docs/DFSAR_POLARIMETRIC_CHANNEL_AUDIT.md Sec 1-2 for full
detail): this environment has genuine raw complex quad-pol pixel access for
exactly TWO acquisitions -- both pipeline-validation-only, confirmed NOT to
cover Cabeus, Wiechert, or any of PRISM's 7 candidates (one is even in the
northern hemisphere, see the audit Sec 6). For every candidate, Cabeus, and
Wiechert, "CPR" is PRISM's existing ISRO-precomputed L3C-MOSAIC band --
genuinely real data, but NEVER self-verified against any Stokes formulation
because no raw pixel access exists for these specific sites here. V3's
Stokes-CPR column is therefore NO DATA for every candidate/control site,
stated honestly rather than estimated.
"""

import json
import os

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(REPO, "outputs", "objective1", "ice_radar_v3_results.json")


# ---------------------------------------------------------------------------
# PART 1 -- real, genuine functions for raw complex-channel data. These are
# fully correct and ready to run the moment real HH/HV/VH/VV pixel arrays
# for a candidate/Cabeus/Wiechert become available (e.g. via an authenticated
# PRADAN session). They are NOT invoked against any candidate/control site in
# this module, because no such pixel data exists in this environment -- see
# module docstring. They ARE invoked, for real, against the one place genuine
# raw pixel data does exist this session (Sec "PIPELINE VALIDATION" below).
# ---------------------------------------------------------------------------

def channel_powers(chans):
    """chans: dict pol -> complex ndarray. Returns real, directly-measured
    per-channel mean power."""
    return {p: float(np.mean(np.abs(a) ** 2)) for p, a in chans.items()}


def stokes_parameters(A, B):
    """A, B: complex ndarrays representing a GENUINE two-component received
    field (e.g. HH,HV for one transmitted H pulse -- see the channel audit
    Sec 5 for why this is the physically correct pairing, vs HH,VV).
    Aggregate (whole-window) construction, matching PRISM's own existing
    aggregate_dop() convention (dop_pipeline_v2_ainsworth_crosstalk.py)."""
    PA = float(np.mean(np.abs(A) ** 2))
    PB = float(np.mean(np.abs(B) ** 2))
    cross = np.mean(A * np.conj(B))
    S1 = PA + PB
    S2 = PA - PB
    S3 = 2 * float(cross.real)
    S4 = -2 * float(cross.imag)
    return S1, S2, S3, S4


def neish_stokes_cpr(S1, S4):
    """Neish et al. 2011's published Stokes-based CPR formulation:
    CPR = (S1-S4)/(S1+S4). Requires S1,S4 constructed from a genuine
    single-transmit dual-linear-receive basis (e.g. HH,HV or VH,VV) to be
    physically meaningful as a circular-polarization ratio -- see channel
    audit Sec 5. Applying it to an (HH,VV) pairing is mathematically
    well-defined but not the physical quantity Neish 2011 describes;
    callers must label results accordingly (done throughout this module)."""
    return (S1 - S4) / (S1 + S4)


def prism_style_dop(S1, S2, S3, S4):
    """PRISM's/Sinha's existing DOP construction, reused unchanged for
    direct comparison. NOT used as a score input anywhere -- diagnostic
    only, per DOP_SINHA_2026_RESEARCH.md."""
    return np.sqrt(S2 ** 2 + S3 ** 2 + S4 ** 2) / S1


def characterize_from_raw(chans_hh_hv_vh_vv):
    """Full real characterization vector from genuine decoded complex
    HH/HV/VH/VV arrays. Returns every requested quantity, computed on the
    two physically-correct bases (HH,HV) and (VH,VV), plus the (HH,VV)
    basis for direct comparison against PRISM's/Sinha's existing
    construction."""
    HH, HV, VH, VV = (chans_hh_hv_vh_vv[p] for p in ["HH", "HV", "VH", "VV"])
    pw = channel_powers({"HH": HH, "HV": HV, "VH": VH, "VV": VV})
    result = {
        "hh_power": pw["HH"], "hv_power": pw["HV"], "vh_power": pw["VH"], "vv_power": pw["VV"],
        "hh_vv_power_ratio": pw["HH"] / pw["VV"],
        "cross_pol_fraction": (pw["HV"] + pw["VH"]) / sum(pw.values()),
        "bases": {},
    }
    for label, (A, B) in {
        "HH_VV_prism_existing_basis": (HH, VV),
        "HH_HV_physically_correct_H_transmit": (HH, HV),
        "VH_VV_physically_correct_V_transmit": (VH, VV),
    }.items():
        S1, S2, S3, S4 = stokes_parameters(A, B)
        result["bases"][label] = {
            "S1": S1, "S2": S2, "S3": S3, "S4": S4,
            "neish_stokes_cpr": neish_stokes_cpr(S1, S4),
            "prism_style_dop": prism_style_dop(S1, S2, S3, S4),
        }
    return result


# ---------------------------------------------------------------------------
# PART 2 -- PIPELINE VALIDATION: real results, computed THIS session, from
# genuine decoded raw complex pixels of the 2021-04-14 acquisition
# (ch2_sar_nrxl_20210414t091917314_d_fp_d18, found in Downloads, extracted,
# byte-structure and channel-mapping independently re-verified -- see
# docs/DFSAR_POLARIMETRIC_CHANNEL_AUDIT.md Sec 3-6). This acquisition is
# CONFIRMED northern-hemisphere and does NOT cover any candidate/control
# site -- these numbers are pipeline validation only, never candidate-
# specific, and are hard-coded here (not re-decoded on every run) because
# the source .dat file (3.2 GB) lives only in this session's scratch temp
# directory, not the repository.
# ---------------------------------------------------------------------------

PIPELINE_VALIDATION_RESULT = {
    "acquisition": "ch2_sar_nrxl_20210414t091917314_d_r0a_xx_fp_xx_d18",
    "confirmed_location": "Northern hemisphere (XML Geometry_Parameters: upper_left_latitude=+85.116 deg, centre_latitude=+86.874 deg -- POSITIVE, unlike every south-polar acquisition PRISM otherwise uses). Does NOT cover Cabeus, Wiechert, or any of PRISM's 7 south-polar candidates.",
    "byte_structure_reverified_independently": {"imaging_offset": 50347, "line_bytes": 2837, "payload_start": 141, "payload_end": 2189, "tail_bytes_0x80": 648},
    "channel_mapping_reverified_independently": {"winning_mapping": {"0": "HV", "1": "HH", "2": "VV", "3": "VH"}, "winning_score": 14.556438663909505, "matches_2025-10-25_product_mapping": True},
    "window": {"line_start": 50000, "line_count": 2000, "n_pixels": 2048000},
    "channel_powers_mean": {"HH": 1926.156005859375, "HV": 73.91981506347656, "VH": 101.59535217285156, "VV": 1867.0374755859375},
    "hh_vv_power_ratio": 1.031664351169429,
    "cross_pol_fraction": 0.04422475489467644,
    "bases": {
        "HH_VV_prism_existing_basis": {"S1": 3793.193359375, "S2": 59.1185302734375, "S3": 2976.72412109375, "S4": -687.8770141601562, "neish_stokes_cpr": 1.4430317878723145, "prism_style_dop": 0.8055854439735413},
        "HH_HV_physically_correct_H_transmit": {"S1": 2000.0758056640625, "S2": 1852.2362060546875, "S3": 0.6534137725830078, "S4": 21.274141311645508, "neish_stokes_cpr": 0.978950560092926, "prism_style_dop": 0.9261441826820374},
        "VH_VV_physically_correct_V_transmit": {"S1": 1968.6328125, "S2": -1765.442138671875, "S3": 25.39369773864746, "S4": -16.700817108154297, "neish_stokes_cpr": 1.017112135887146, "prism_style_dop": 0.896918773651123},
    },
    "interpretation": "The (HH,VV) basis (PRISM's/Sinha's existing pairing) gives Neish-CPR=1.443; the two physically-correct single-transmit bases give 0.979 and 1.017 -- a ~45% relative difference from the SAME raw pixels, purely from which channels are paired into the Stokes vector. This is real, freshly-computed evidence that basis choice is not cosmetic. Not ice-relevant (wrong hemisphere) -- pipeline validation only.",
}


# ---------------------------------------------------------------------------
# PART 3 -- real, already-existing PRISM CPR (ISRO L3C-MOSAIC band) for
# every candidate/control/reference site, for the requested "PRISM CPR vs
# V3 Stokes CPR" comparison table. V3 Stokes CPR is NO DATA for all of
# these (see Part 1 docstring / channel audit) -- reported honestly, not
# estimated. Source: same real pipeline runs already used throughout this
# investigation (radar_pipeline.py / validation_pipeline.py real outputs).
# ---------------------------------------------------------------------------

SITES_PRISM_CPR = {
    # 7 PRISM candidates (interior mean, shortlist_full_res_comparison.csv)
    "SP_840980_0797630": {"role": "PRISM candidate (primary)", "prism_cpr": 0.6303874, "m3_status": "NOT TESTED"},
    "SP_832640_0090770": {"role": "PRISM candidate", "prism_cpr": 0.7104936, "m3_status": "NOT TESTED"},
    "SP_830080_0535120": {"role": "PRISM candidate", "prism_cpr": 0.6684831, "m3_status": "NOT TESTED"},
    "SP_842420_0421060": {"role": "PRISM candidate", "prism_cpr": 0.5563170, "m3_status": "NOT TESTED"},
    "SP_817950_1586580": {"role": "PRISM candidate", "prism_cpr": 0.5183735, "m3_status": "NOT TESTED"},
    "SP_819860_1568660": {"role": "PRISM candidate", "prism_cpr": 0.6359729, "m3_status": "NOT TESTED"},
    "SP_809570_2454450": {"role": "PRISM candidate", "prism_cpr": 0.3954223, "m3_status": "NOT TESTED"},
    # Controls + M3 reference sites (whole-window mean, ice_reference_sites.csv / control_sites.csv)
    "LCROSS_Cabeus": {"role": "POSITIVE CONTROL (LCROSS)", "prism_cpr": 0.1662777, "m3_status": "NOT ADDRESSED (not in Li et al. 2018's crater lists)"},
    "Wiechert": {"role": "NEGATIVE CONTROL (M3)", "prism_cpr": 0.3109077, "m3_status": "CONFIRMED NEGATIVE"},
    "Faustini": {"role": "M3 positive", "prism_cpr": 0.2967567, "m3_status": "CONFIRMED POSITIVE"},
    "De_Gerlache": {"role": "M3 positive", "prism_cpr": 0.3223958, "m3_status": "CONFIRMED POSITIVE"},
    "Haworth": {"role": "M3 positive", "prism_cpr": 0.2382054, "m3_status": "CONFIRMED POSITIVE"},
    "Shoemaker": {"role": "M3 positive", "prism_cpr": 0.2006540, "m3_status": "CONFIRMED POSITIVE"},
    "Sverdrup": {"role": "M3 positive", "prism_cpr": 0.2495164, "m3_status": "CONFIRMED POSITIVE"},
    "Shackleton": {"role": "M3 positive", "prism_cpr": 0.4799910, "m3_status": "CONFIRMED POSITIVE"},
    "Amundsen": {"role": "M3 negative (contested, see docs)", "prism_cpr": 0.3008572, "m3_status": "CONFIRMED NEGATIVE (contested by Brown et al. 2022)"},
    "Hedervari": {"role": "M3 negative", "prism_cpr": 0.2399840, "m3_status": "CONFIRMED NEGATIVE"},
    "Idelson_L": {"role": "M3 negative", "prism_cpr": 0.2716206, "m3_status": "CONFIRMED NEGATIVE"},
}


def build_cpr_comparison_table():
    """Task-requested table: PRISM CPR vs V3 Stokes CPR, per site. V3 column
    is NO DATA everywhere here -- no raw pixel access for any of these
    sites in this environment (see module docstring)."""
    rows = []
    for sid, s in SITES_PRISM_CPR.items():
        rows.append({
            "site_id": sid, "role": s["role"], "m3_status": s["m3_status"],
            "prism_cpr_L3C_MOSAIC_band": s["prism_cpr"],
            "v3_stokes_cpr": None,
            "absolute_difference": None,
            "relative_difference": None,
            "reason_v3_not_computable": "No raw/SLC complex quad-pol pixel data accessible for this site in this environment (ISRO PRADAN login-gated; no local cache) -- see docs/DFSAR_POLARIMETRIC_CHANNEL_AUDIT.md Sec 1-2.",
        })
    return rows


def m3_positive_vs_negative_cpr_check():
    """Second validation (task Sec): does PRISM's real, existing CPR data
    (whatever ISRO's internal formula is) separate M3-positive from
    M3-negative sites at all? Real arithmetic on real, already-computed
    numbers -- no fitting, no tuning."""
    positive_ids = ["LCROSS_Cabeus", "Faustini", "De_Gerlache", "Haworth", "Shoemaker", "Sverdrup", "Shackleton"]
    negative_ids = ["Wiechert", "Amundsen", "Hedervari", "Idelson_L"]
    pos_cpr = [SITES_PRISM_CPR[s]["prism_cpr"] for s in positive_ids]
    neg_cpr = [SITES_PRISM_CPR[s]["prism_cpr"] for s in negative_ids]
    return {
        "positive_sites": {sid: SITES_PRISM_CPR[sid]["prism_cpr"] for sid in positive_ids},
        "negative_sites": {sid: SITES_PRISM_CPR[sid]["prism_cpr"] for sid in negative_ids},
        "positive_mean_cpr": float(np.mean(pos_cpr)), "positive_std_cpr": float(np.std(pos_cpr)),
        "negative_mean_cpr": float(np.mean(neg_cpr)), "negative_std_cpr": float(np.std(neg_cpr)),
        "highest_cpr_site": max(SITES_PRISM_CPR.items(), key=lambda kv: kv[1]["prism_cpr"] if kv[0] in positive_ids + negative_ids else -1)[0],
        "lowest_cpr_site": min(SITES_PRISM_CPR.items(), key=lambda kv: kv[1]["prism_cpr"] if kv[0] in positive_ids + negative_ids else 999)[0],
        "note": "Real arithmetic on real, already-computed PRISM CPR values (ISRO L3C-MOSAIC band). No fitting or tuning performed.",
    }


def radar_ice_consistency_classification():
    """Task-requested classification for the 7 candidates: HIGH/MODERATE/
    LOW/UNRESOLVED, ONLY if justified from literature -- else UNRESOLVED.
    Justification for defaulting to UNRESOLVED for all 7, stated per site:
    (1) no incidence-angle normalization is possible (channel audit Sec 7);
    (2) no validated quantitative roughness-CPR model exists that PRISM's
    data can apply (docs/ICE_METRIC_LITERATURE_MAP.md); (3) the second
    validation above shows CPR does not separate M3-positive from
    M3-negative sites in PRISM's own real data (positive/negative means are
    nearly identical); (4) no genuine Stokes-CPR can be computed for any of
    the 7 (no raw pixel access). Given all four, no candidate's CPR value
    can be interpreted as evidence of anything beyond what its own
    magnitude already conveys -- which the literature (Neish 2011, Carter
    2012, Eke 2014, Fa 2018) establishes is not reliably ice-related."""
    m3_check = m3_positive_vs_negative_cpr_check()
    separation = abs(m3_check["positive_mean_cpr"] - m3_check["negative_mean_cpr"])
    candidates = ["SP_840980_0797630", "SP_832640_0090770", "SP_830080_0535120",
                  "SP_842420_0421060", "SP_817950_1586580", "SP_819860_1568660", "SP_809570_2454450"]
    out = {}
    for cid in candidates:
        out[cid] = {
            "prism_cpr": SITES_PRISM_CPR[cid]["prism_cpr"],
            "classification": "UNRESOLVED",
            "justification": (
                f"CPR does not separate PRISM's own M3-positive (mean {m3_check['positive_mean_cpr']:.3f}) "
                f"from M3-negative (mean {m3_check['negative_mean_cpr']:.3f}) reference sites "
                f"(difference {separation:.3f}, smaller than either group's own std). "
                "No incidence-angle correction, no validated roughness model, and no genuine "
                "raw-channel Stokes-CPR are computable for this site in this environment. "
                "A CPR value alone cannot be classified as ice-consistent evidence at any level "
                "without at least one of these missing pieces."
            ),
        }
    return out


def main():
    print("=== Channel audit summary: see docs/DFSAR_POLARIMETRIC_CHANNEL_AUDIT.md ===\n")

    print("=== Pipeline validation (real decoded pixels, non-candidate acquisition) ===")
    print(json.dumps(PIPELINE_VALIDATION_RESULT["bases"], indent=2))

    cpr_table = build_cpr_comparison_table()
    print("\n=== PRISM CPR vs V3 Stokes CPR (per site) ===")
    for row in cpr_table:
        print(f"{row['site_id']:<22} PRISM_CPR={row['prism_cpr_L3C_MOSAIC_band']:.4f}  V3_Stokes_CPR={row['v3_stokes_cpr']}")

    m3check = m3_positive_vs_negative_cpr_check()
    print("\n=== M3-positive vs M3-negative real CPR comparison ===")
    print(f"Positive mean CPR: {m3check['positive_mean_cpr']:.4f} +/- {m3check['positive_std_cpr']:.4f}")
    print(f"Negative mean CPR: {m3check['negative_mean_cpr']:.4f} +/- {m3check['negative_std_cpr']:.4f}")
    print(f"Highest-CPR site overall: {m3check['highest_cpr_site']}  Lowest-CPR site overall: {m3check['lowest_cpr_site']}")

    classification = radar_ice_consistency_classification()
    print("\n=== RADAR ICE CONSISTENCY (7 candidates) ===")
    for cid, r in classification.items():
        print(f"{cid:<22} {r['classification']}")

    out = {
        "channel_audit_reference": "docs/DFSAR_POLARIMETRIC_CHANNEL_AUDIT.md",
        "pipeline_validation_non_candidate": PIPELINE_VALIDATION_RESULT,
        "prism_cpr_vs_v3_stokes_cpr_table": cpr_table,
        "m3_positive_vs_negative_cpr_check": m3check,
        "radar_ice_consistency_7_candidates": classification,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved: {OUT_PATH}")


if __name__ == "__main__":
    main()
