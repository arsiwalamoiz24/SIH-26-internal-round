"""
PRISM Objective 1 -- DFSAR raw L0A polarization channel-mapping verification.

Phase 1 (2026-08-22), task: "Verify DFSAR polarization channel mapping against
the product metadata."

This reproduces the byte-level decode established in
notebooks/objective1_y4r_polarimetry.ipynb.ipynb (STEP 8-19) EXACTLY (same
IMAGING_OFFSET, LINE_BYTES, PAYLOAD_START/END, same 4-way line interleave,
same bias-correction formula) against the same raw product
(ch2_sar_nrxl_20251025t211236510_d_r0a_xx_fp_xx_d18.dat), now available locally.

No scientific formula is changed from the original notebook. Two things are
added, both explicitly flagged as open questions in PROJECT_STATUS.md Section 3.2:

  1. An exhaustive permutation search over which of the 4 interleaved byte-groups
     (G0..G3) maps to which polarization (HH/HV/VH/VV), scored against the XML's
     std_real/std_imag/bias_real/bias_imag reference values. The original notebook
     picked ONE mapping (G0->HV, G1->HH, G2->VV, G3->VH) by inspection and did not
     check whether a different assignment fits the XML metadata better. This
     script checks all 24 permutations and reports the best fit.
  2. The original notebook used only the first 100 raw imaging lines (25 lines per
     polarization group) -- 0.008% of the 1,256,410-line product. This script
     repeats the same computation with N_LINES=4000 (1000 lines per group) purely
     to check whether the channel identification and its confidence level are
     stable with a larger, still-cheap sample. This is a sample-size increase,
     not a formula change.
"""

import itertools
import json
import os

import numpy as np

RAW_DAT = r"C:\Users\radhe\PRISM_local_data\raw\ch2_sar_nrxl_20251025t211236510_d_r0a_xx_fp_xx_d18.dat"
OUT_DIR = r"C:\Users\radhe\OneDrive\Documents\GitHub\SIH-26-internal-round\PRISM\outputs\objective1"
os.makedirs(OUT_DIR, exist_ok=True)

IMAGING_OFFSET = 48158
LINE_BYTES = 2325
PAYLOAD_START = 141
PAYLOAD_END = 2189  # exclusive; 2048 bytes = 1024 IQ samples

XML_STATS = {
    "HH": {"std_real": 12.502030, "std_imag": 12.504541, "bias_real": 0.086681, "bias_imag": 2.846410},
    "HV": {"std_real": 4.048946, "std_imag": 4.232149, "bias_real": 0.206393, "bias_imag": 2.980114},
    "VH": {"std_real": 5.209197, "std_imag": 5.187600, "bias_real": -1.551034, "bias_imag": 1.179173},
    "VV": {"std_real": 11.240361, "std_imag": 10.801348, "bias_real": 3.465097, "bias_imag": 5.086929},
}

ORIGINAL_MAPPING = {"G0": "HV", "G1": "HH", "G2": "VV", "G3": "VH"}

BIAS_SCALE = {
    "bias_real": float(np.std([XML_STATS[p]["bias_real"] for p in XML_STATS])),
    "bias_imag": float(np.std([XML_STATS[p]["bias_imag"] for p in XML_STATS])),
}


def load_groups(n_lines):
    with open(RAW_DAT, "rb") as f:
        f.seek(IMAGING_OFFSET)
        raw = f.read(n_lines * LINE_BYTES)
    lines = np.frombuffer(raw, dtype=np.uint8).reshape(n_lines, LINE_BYTES)
    payload = lines[:, PAYLOAD_START:PAYLOAD_END]
    I = payload[:, 0::2].astype(np.float64) - 128.0
    Q = payload[:, 1::2].astype(np.float64) - 128.0
    complex_data = I + 1j * Q
    groups = {
        "G0": complex_data[0::4],
        "G1": complex_data[1::4],
        "G2": complex_data[2::4],
        "G3": complex_data[3::4],
    }
    return groups


def group_stats(g):
    return {
        "std_real": float(np.std(g.real)), "std_imag": float(np.std(g.imag)),
        "bias_real": float(np.mean(g.real)), "bias_imag": float(np.mean(g.imag)),
    }


def fit_error(group_s, xml_s):
    # std_real/std_imag: relative squared error is stable here -- all 4 XML
    # reference std values (4.0-12.5) are safely away from zero.
    #
    # bias_real/bias_imag: relative error is UNSTABLE here. HH's XML bias_real
    # is 0.086681 -- almost zero -- so a modest absolute mismatch (e.g. 0.4)
    # gets squared and divided by ~0.087, producing a relative error >20 that
    # swamps every other term and makes the fit metric meaningless. This was
    # caught by inspection of a first version of this script (which ranked the
    # original notebook's mapping as only 2nd-best, entirely because of this
    # instability on the HH bias_real term -- not because the mapping is
    # actually a worse fit). Fixed by scoring bias terms with squared error
    # normalized by the cross-channel spread of that statistic (a fixed,
    # non-zero scale shared by all 4 channels), instead of each channel's own
    # (possibly near-zero) reference value.
    err = 0.0
    for key in ("std_real", "std_imag"):
        denom = xml_s[key] if abs(xml_s[key]) > 1e-6 else 1.0
        err += ((group_s[key] - xml_s[key]) / denom) ** 2
    for key in ("bias_real", "bias_imag"):
        scale = BIAS_SCALE[key]
        err += ((group_s[key] - xml_s[key]) / scale) ** 2
    return err


def evaluate_mapping(groups, mapping):
    total_err = 0.0
    per_pol = {}
    for group_name, pol in mapping.items():
        gs = group_stats(groups[group_name])
        e = fit_error(gs, XML_STATS[pol])
        per_pol[pol] = {"group": group_name, "stats": gs, "fit_error": e}
        total_err += e
    return total_err, per_pol


def permutation_search(groups):
    group_names = ["G0", "G1", "G2", "G3"]
    pol_names = ["HH", "HV", "VH", "VV"]
    results = []
    for perm in itertools.permutations(pol_names):
        mapping = dict(zip(group_names, perm))
        total_err, per_pol = evaluate_mapping(groups, mapping)
        results.append({"mapping": mapping, "total_fit_error": total_err, "per_pol": per_pol})
    results.sort(key=lambda r: r["total_fit_error"])
    return results


def run(n_lines, label):
    print(f"\n=== {label}: N_LINES={n_lines} ({n_lines // 4} lines/group) ===")
    groups = load_groups(n_lines)
    results = permutation_search(groups)

    best = results[0]
    original_result = next(r for r in results if r["mapping"] == ORIGINAL_MAPPING)
    original_rank = results.index(original_result) + 1

    print(f"Best-fit mapping:     {best['mapping']}  (total_fit_error={best['total_fit_error']:.6f})")
    print(f"Original mapping:     {ORIGINAL_MAPPING}  (total_fit_error={original_result['total_fit_error']:.6f}, rank {original_rank}/24)")
    print("Per-polarization fit error, original mapping:")
    for pol, info in original_result["per_pol"].items():
        print(f"  {pol} <- {info['group']}: fit_error={info['fit_error']:.6f}  stats={info['stats']}")

    return {
        "n_lines": n_lines,
        "lines_per_group": n_lines // 4,
        "best_mapping": best["mapping"],
        "best_fit_error": best["total_fit_error"],
        "original_mapping": ORIGINAL_MAPPING,
        "original_fit_error": original_result["total_fit_error"],
        "original_mapping_rank_out_of_24": original_rank,
        "original_mapping_per_pol_detail": original_result["per_pol"],
        "top_5_mappings": [{"mapping": r["mapping"], "total_fit_error": r["total_fit_error"]} for r in results[:5]],
    }


def main():
    report = {}
    report["n100_reproduction"] = run(100, "Reproduction of notebook's original 100-line test")
    report["n4000_larger_sample"] = run(4000, "Extended 4000-line sample (1000 lines/group)")

    agree = (report["n100_reproduction"]["best_mapping"] == report["n4000_larger_sample"]["best_mapping"])
    report["best_mapping_stable_across_sample_sizes"] = agree
    report["original_mapping_is_best_fit_at_n100"] = (report["n100_reproduction"]["original_mapping_rank_out_of_24"] == 1)
    report["original_mapping_is_best_fit_at_n4000"] = (report["n4000_larger_sample"]["original_mapping_rank_out_of_24"] == 1)

    with open(os.path.join(OUT_DIR, "dfsar_channel_mapping_verification.json"), "w") as f:
        json.dump(report, f, indent=2, default=str)

    print("\n=== SUMMARY ===")
    print("Best mapping stable across 100 -> 4000 lines:", agree)
    print("Original notebook mapping is the best fit at N=100:", report["original_mapping_is_best_fit_at_n100"])
    print("Original notebook mapping is the best fit at N=4000:", report["original_mapping_is_best_fit_at_n4000"])
    print("\nWritten to", os.path.join(OUT_DIR, "dfsar_channel_mapping_verification.json"))


if __name__ == "__main__":
    main()
