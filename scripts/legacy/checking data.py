"""
=======================================================
  ISRO SAR Data Validator — Lunar Ice Detection Project
=======================================================
USAGE:
  python check_data.py <path_to_downloaded_folder>

EXAMPLES:
  python check_data.py "ch2_sar_ncxl_20250914t234020438_d_cp_d18"
  python check_data.py "ch2_sar_nfxl_20240820t195745092_d_fp_d18"

This script will tell you exactly:
  - What files are inside
  - Whether DOP can be computed (needs complex LH + LV)
  - Whether Pv / CPR can be computed (needs vol, odd, evn)
  - What ML pipelines you can run
=======================================================
"""

import os
import sys
import glob

try:
    import rasterio
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False

KNOWN_PATTERNS = {
    "_cp_lh_": ("CP LH Channel",       "dop"),
    "_cp_lv_": ("CP LV Channel",       "dop"),
    "_fp_vol_": ("FP Volume Scatter",  "pv_cpr"),
    "_fp_odd_": ("FP Odd Bounce",      "pv_cpr"),
    "_fp_evn_": ("FP Even Bounce",     "pv_cpr"),
    "_fp_hlx_": ("FP Helix Scatter",   "pv_cpr"),
    "_fp_hh_": ("FP HH Channel",       "cpr_hh"),
    "_fp_vv_": ("FP VV Channel",       "cpr_hh"),
    "_fp_hv_": ("FP HV Channel",       "cpr_hh"),
    "_fp_vh_": ("FP VH Channel",       "cpr_hh"),
    "_in_cp_":  ("Incidence Angle (CP)", "geometry"),
    "_in_fp_":  ("Incidence Angle (FP)", "geometry"),
    "_ma_cp_":  ("Mask (CP)",           "geometry"),
    "_ma_fp_":  ("Mask (FP)",           "geometry"),
}

def inspect_tif(path):
    info = {
        "size_mb": os.path.getsize(path) / (1024 * 1024),
        "bands": None,
        "dtype": None,
        "is_complex": False,
        "shape": None,
        "error": None,
    }
    if HAS_RASTERIO:
        try:
            with rasterio.open(path) as src:
                info["bands"]      = src.count
                info["dtype"]      = src.dtypes[0]
                info["shape"]      = (src.height, src.width)
                info["is_complex"] = "complex" in src.dtypes[0].lower()
                if src.count == 2 and ("uint16" in src.dtypes[0] or "float" in src.dtypes[0]):
                    info["is_complex"] = True
        except Exception as e:
            info["error"] = str(e)
    return info

def validate_folder(folder):
    print()
    print("=" * 60)
    print("  ISRO SAR DATA VALIDATOR")
    print("=" * 60)
    print("  Folder: " + folder)
    print()

    if not os.path.isdir(folder):
        print("  ERROR: Folder not found -> " + folder)
        return

    tif_files = glob.glob(os.path.join(folder, "**", "*.tif"), recursive=True)
    xml_files = glob.glob(os.path.join(folder, "**", "*.xml"), recursive=True)

    print("  Found " + str(len(tif_files)) + " TIF files, " + str(len(xml_files)) + " XML files")
    print()

    if not tif_files:
        print("  No TIF files found. Is this the right folder?")
        return

    found = {
        "dop":     [],
        "pv_cpr":  [],
        "cpr_hh":  [],
        "geometry":[],
        "unknown": [],
    }

    print("  FILES DETECTED:")
    print("  " + "-" * 55)

    for tif in sorted(tif_files):
        fname    = os.path.basename(tif).lower()
        label    = "Unknown"
        category = "unknown"

        for pattern, (desc, cat) in KNOWN_PATTERNS.items():
            if pattern in fname:
                label    = desc
                category = cat
                break

        info = inspect_tif(tif)
        found[category].append({"path": tif, "label": label, "info": info})

        size_str  = "{:.1f} MB".format(info["size_mb"])
        dtype_str = info["dtype"] if info["dtype"] else "unknown"
        cpx_str   = " [COMPLEX]" if info["is_complex"] else " [INTENSITY]"
        shape_str = "{}x{}".format(info["shape"][0], info["shape"][1]) if info["shape"] else ""

        print("  [" + category.upper().ljust(8) + "] " + os.path.basename(tif))
        print("             -> " + label + " | " + size_str + " | " + dtype_str + cpx_str + " | " + shape_str)
        if info["error"]:
            print("             -> ERROR: " + info["error"])
        print()

    dop_lh = [f for f in found["dop"] if "_cp_lh_" in f["path"].lower()]
    dop_lv = [f for f in found["dop"] if "_cp_lv_" in f["path"].lower()]
    has_lh_complex = any(f["info"]["is_complex"] for f in dop_lh) if dop_lh else False
    has_lv_complex = any(f["info"]["is_complex"] for f in dop_lv) if dop_lv else False

    fp_vol = [f for f in found["pv_cpr"] if "_fp_vol_" in f["path"].lower()]
    fp_odd = [f for f in found["pv_cpr"] if "_fp_odd_" in f["path"].lower()]
    fp_evn = [f for f in found["pv_cpr"] if "_fp_evn_" in f["path"].lower()]
    fp_hh  = [f for f in found["cpr_hh"] if "_fp_hh_" in f["path"].lower()]
    fp_hv  = [f for f in found["cpr_hh"] if "_fp_hv_" in f["path"].lower()]

    print("=" * 60)
    print("  WHAT CAN WE COMPUTE?")
    print("=" * 60)

    print()
    print("  [1] DOP (Degree of Polarization) --- needs LH + LV complex")
    if dop_lh and dop_lv and has_lh_complex and has_lv_complex:
        print("      STATUS: READY -- Both LH and LV are complex. DOP can be computed!")
    elif dop_lh and dop_lv:
        print("      STATUS: PARTIAL -- LH and LV found but INTENSITY only (no phase).")
        print("              Need the SLC product, not the _gri_ or _sri_ product.")
    elif dop_lv and not dop_lh:
        print("      STATUS: BLOCKED -- LV found but LH is MISSING from zip.")
        print("              Re-download the full ZIP from ISRO PRADAN.")
    elif dop_lh and not dop_lv:
        print("      STATUS: BLOCKED -- LH found but LV is MISSING.")
    else:
        print("      STATUS: NOT AVAILABLE -- No CP channels found in this folder.")
        print("              This might be an FP product. Download a _cp_ product for DOP.")

    print()
    print("  [2] Pv + CPR --- needs vol + odd + evn decomposition files")
    if fp_vol and fp_odd and fp_evn:
        print("      STATUS: READY -- All FP decomposition files present!")
    elif fp_vol or fp_odd or fp_evn:
        missing = []
        if not fp_vol: missing.append("vol")
        if not fp_odd: missing.append("odd")
        if not fp_evn: missing.append("evn")
        print("      STATUS: PARTIAL -- Missing: " + ", ".join(missing))
    else:
        print("      STATUS: NOT AVAILABLE -- No FP decomposition files found.")
        print("              Download an FP (Full Polarimetry) product for Pv/CPR.")

    print()
    print("  [3] CPR from raw HH/HV --- needs HH + HV channels")
    if fp_hh and fp_hv:
        print("      STATUS: READY -- HH and HV present. CPR = HV/HH possible.")
    elif fp_hh or fp_hv:
        print("      STATUS: PARTIAL -- Only one channel found.")
    else:
        print("      STATUS: NOT AVAILABLE -- No HH/HV channels found.")

    print()
    print("  [4] ISOLATION FOREST (AI/ML Ice Detector)")
    can_iso = (fp_vol and fp_odd and fp_evn) or (dop_lh and dop_lv and has_lh_complex and has_lv_complex)
    if can_iso:
        print("      STATUS: READY -- Features available! Isolation Forest can be trained.")
    else:
        print("      STATUS: WAITING -- Need DOP or Pv first before training.")

    print()
    print("=" * 60)
    print("  FINAL VERDICT")
    print("=" * 60)
    score = 0
    dop_ok = dop_lh and dop_lv and has_lh_complex and has_lv_complex
    pv_ok  = fp_vol and fp_odd and fp_evn
    geo_ok = bool(found["geometry"])

    if dop_ok:
        score += 2
        print("  [PASS] DOP: READY")
    else:
        print("  [FAIL] DOP: NOT READY")

    if pv_ok:
        score += 2
        print("  [PASS] Pv/CPR: READY")
    else:
        print("  [FAIL] Pv/CPR: NOT READY")

    if geo_ok:
        score += 1
        print("  [PASS] Incidence Angle: PRESENT")
    else:
        print("  [WARN] Incidence Angle: MISSING")

    print()
    if score >= 4:
        print("  >>> THIS FILE IS USEFUL - You can compute DOP + Pv and train Isolation Forest <<<")
    elif score >= 2:
        print("  >>> PARTIALLY USEFUL - Some metrics available but not all <<<")
    else:
        print("  >>> NOT ENOUGH DATA - Try a different product from ISRO PRADAN <<<")
    print()
    print("=" * 60)

if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) >= 2 else os.getcwd()
    validate_folder(folder)
