"""
PRISM independent validation -- consolidate validation_pipeline.py's raw
results into the required deliverables. Read-only aggregation; no new
calculations against PRISM's candidate pipeline, no threshold changes.
"""

import json
import os

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = r"C:\Users\radhe\OneDrive\Documents\GitHub\SIH-26-internal-round\PRISM"
OUT_DIR = os.path.join(REPO, "outputs", "validation")

with open(os.path.join(OUT_DIR, "validation_raw_results.json")) as f:
    raw = json.load(f)


def crater_area_km2(diam):
    if diam is None:
        return None
    r = diam / 2.0
    return round(np.pi * r * r, 2)


# ---- site CSVs ----
rows = []
for r in raw:
    rows.append({
        "site_id": r["site_id"], "name": r["name"], "category": r["category"],
        "lat_deg": r["lat"], "lon_deg": r["lon"], "region": r["region"],
        "diameter_km": r.get("diameter_km"),
        "reference_area_km2_crater_disk": crater_area_km2(r.get("diameter_km")),
        "window_half_km": r["window_half_km"],
        "source_mission": r["source_mission"], "source_publication": r["source_publication"],
        "evidence_type": r["evidence_type"], "confidence": r["confidence"],
        "coordinate_source": r["coordinate_source"], "notes": r.get("notes", ""),
        "prism_status": r["status"],
        "in_psr_catalog": r.get("in_psr_catalog"), "psr_id": r.get("psr_id"),
        "y4r_cpr_serd_tratio_coverage": r["status"] == "OK",
        "dfsar_dop_coverage": "NOT TESTED" if r["status"] == "OK" else "NO_COVERAGE (region)",
        "pv_mean": r.get("pv", {}).get("mean") if r["status"] == "OK" else None,
        "pv_median": r.get("pv", {}).get("median") if r["status"] == "OK" else None,
        "cpr_mean": r.get("cpr", {}).get("mean") if r["status"] == "OK" else None,
        "cpr_median": r.get("cpr", {}).get("median") if r["status"] == "OK" else None,
        "serd_mean": r.get("serd", {}).get("mean") if r["status"] == "OK" else None,
        "serd_median": r.get("serd", {}).get("median") if r["status"] == "OK" else None,
        "tratio_mean": r.get("tratio", {}).get("mean") if r["status"] == "OK" else None,
        "tratio_median": r.get("tratio", {}).get("median") if r["status"] == "OK" else None,
        "slope_deg_mean": (r.get("slope_deg") or {}).get("mean") if r["status"] == "OK" else None,
        "n_valid_px_pv": r.get("pv", {}).get("n_valid_px") if r["status"] == "OK" else None,
        "pct_nan_pv": r.get("pv", {}).get("pct_nan") if r["status"] == "OK" else None,
        "physics_evidence_score_analog": r.get("physics_evidence_score_analog"),
    })

df = pd.DataFrame(rows)
pos_df = df[df.category == "positive"].copy()
ctrl_df = df[df.category == "control"].copy()
pos_df.to_csv(os.path.join(OUT_DIR, "ice_reference_sites.csv"), index=False)
ctrl_df.to_csv(os.path.join(OUT_DIR, "control_sites.csv"), index=False)
print("wrote ice_reference_sites.csv (%d rows), control_sites.csv (%d rows)" % (len(pos_df), len(ctrl_df)))

# ---- geojson (crater-disk polygons for sites with a diameter; LCROSS as a point) ----
import math

def circle_polygon_lonlat(lat, lon, radius_km, n=48):
    # approximate small-circle in lat/lon around a polar site (good enough for a reference-area visualization at this scale)
    R_moon = 1737.4
    coords = []
    for i in range(n + 1):
        theta = 2 * math.pi * i / n
        dlat = (radius_km / R_moon) * (180 / math.pi) * math.cos(theta)
        dlon = (radius_km / R_moon) * (180 / math.pi) * math.sin(theta) / max(math.cos(math.radians(lat)), 1e-6)
        coords.append([lon + dlon, lat + dlat])
    return coords

features = []
for r in raw:
    if r.get("diameter_km"):
        poly = circle_polygon_lonlat(r["lat"], r["lon"], r["diameter_km"] / 2.0)
        geom = {"type": "Polygon", "coordinates": [poly]}
    else:
        geom = {"type": "Point", "coordinates": [r["lon"], r["lat"]]}
    features.append({
        "type": "Feature", "geometry": geom,
        "properties": {"site_id": r["site_id"], "name": r["name"], "category": r["category"],
                       "diameter_km": r.get("diameter_km"),
                       "reference_area_km2_crater_disk": crater_area_km2(r.get("diameter_km")),
                       "note": "Polygon = crater disk approximation (small-circle around center coordinate), NOT the true M3 ice-pixel footprint, which is not published in machine-readable form (see docs/INDEPENDENT_ICE_VALIDATION.md)."},
    })
geojson = {"type": "FeatureCollection", "features": features}
with open(os.path.join(OUT_DIR, "ice_reference_area.geojson"), "w") as f:
    json.dump(geojson, f, indent=2)
print("wrote ice_reference_area.geojson (%d features)" % len(features))

# ---- validation_metrics.json ----
def dist_summary(vals):
    vals = [v for v in vals if v is not None and np.isfinite(v)]
    if not vals:
        return None
    arr = np.array(vals)
    return {"n": len(arr), "mean": float(arr.mean()), "median": float(np.median(arr)),
            "std": float(arr.std()), "min": float(arr.min()), "max": float(arr.max()),
            "values": [float(v) for v in arr]}

metrics = {"n_sites_total": len(raw),
           "n_positive": int((df.category == "positive").sum()),
           "n_control": int((df.category == "control").sum()),
           "n_no_coverage_north_pole": int((df.prism_status == "NO_COVERAGE").sum()),
           "n_tested_positive": int(((df.category == "positive") & (df.prism_status == "OK")).sum()),
           "n_tested_control": int(((df.category == "control") & (df.prism_status == "OK")).sum())}

for metric_col, label in [("pv_mean", "Pv"), ("cpr_mean", "CPR"), ("serd_mean", "SERD"),
                           ("tratio_mean", "T_Ratio"), ("physics_evidence_score_analog", "physics_evidence_score_analog")]:
    metrics[label] = {
        "positive": dist_summary(pos_df[pos_df.prism_status == "OK"][metric_col].tolist()),
        "control": dist_summary(ctrl_df[ctrl_df.prism_status == "OK"][metric_col].tolist()),
    }

# overlap / ranking: pool all tested sites, rank by evidence score
tested = df[df.prism_status == "OK"].copy()
tested = tested.sort_values("physics_evidence_score_analog", ascending=False).reset_index(drop=True)
tested["rank"] = tested.index + 1
metrics["pooled_ranking_by_evidence_score"] = tested[["rank", "site_id", "category", "physics_evidence_score_analog", "pv_mean", "cpr_mean", "in_psr_catalog"]].to_dict(orient="records")

pos_scores = pos_df[pos_df.prism_status == "OK"]["physics_evidence_score_analog"].dropna().values
ctrl_scores = ctrl_df[ctrl_df.prism_status == "OK"]["physics_evidence_score_analog"].dropna().values
metrics["systematic_separation_check"] = {
    "positive_mean_score": float(pos_scores.mean()) if len(pos_scores) else None,
    "control_mean_score": float(ctrl_scores.mean()) if len(ctrl_scores) else None,
    "positive_median_score": float(np.median(pos_scores)) if len(pos_scores) else None,
    "control_median_score": float(np.median(ctrl_scores)) if len(ctrl_scores) else None,
    "n_positive_above_control_median": int((pos_scores > np.median(ctrl_scores)).sum()) if len(ctrl_scores) and len(pos_scores) else None,
    "verdict": None,  # filled below
}
if len(pos_scores) and len(ctrl_scores):
    if pos_scores.mean() > ctrl_scores.mean():
        metrics["systematic_separation_check"]["verdict"] = "Positive sites score higher on average than control sites in this small sample -- consistent with (not proof of) the hypothesis."
    else:
        metrics["systematic_separation_check"]["verdict"] = "Positive sites do NOT score higher on average than control sites in this sample -- reported honestly, this does NOT support the hypothesis that PRISM's radar evidence score systematically separates independently-identified ice sites from checked-negative controls."

metrics["dop_coverage_note"] = "DOP was not computed for any of these 13 reference sites. Doing so would require repeating the acquisition-hunt-and-download workflow used for the original candidate (search 602-manifest true-image-footprint corners + Grid CSV, download ~1-5GB per confirmed acquisition) for each site -- not attempted in this task, per explicit scope."
metrics["m3_pixel_level_data_availability"] = "INSUFFICIENT for quantitative pixel-level validation. Li et al. 2018 PNAS (the only M3 ice-detection publication located) presents ice detections only as a map/figure (SI Appendix Fig. S5, ice exposures overlain on Diviner temperature map) with NO machine-readable coordinate table of individual ice-bearing pixels in the main text or the full 23-page SI Appendix (verified by downloading and full-text-searching the actual SI PDF this session, outputs/validation/refs/pnas.1802345115.sapp.pdf). This validation instead uses CRATER-LEVEL references (named craters the paper reports positive/negative for), which is a real, documented approximation, not the pixel-level dataset the task requested."

with open(os.path.join(OUT_DIR, "validation_metrics.json"), "w") as f:
    json.dump(metrics, f, indent=2, default=str)
print("wrote validation_metrics.json")
print(json.dumps(metrics["systematic_separation_check"], indent=2))

# ---- plot ----
fig, axes = plt.subplots(1, 5, figsize=(22, 5))
metric_pairs = [("pv_mean", "Pv"), ("cpr_mean", "CPR"), ("serd_mean", "SERD"), ("tratio_mean", "T-Ratio"), ("physics_evidence_score_analog", "Evidence Score")]
for ax, (col, label) in zip(axes, metric_pairs):
    pos_vals = pos_df[pos_df.prism_status == "OK"][col].dropna().values
    ctrl_vals = ctrl_df[ctrl_df.prism_status == "OK"][col].dropna().values
    bp = ax.boxplot([pos_vals, ctrl_vals], tick_labels=["ICE-REF\n(n=%d)" % len(pos_vals), "CONTROL\n(n=%d)" % len(ctrl_vals)], patch_artist=True)
    bp["boxes"][0].set_facecolor("#d95f5f"); bp["boxes"][1].set_facecolor("#5f9fd9")
    for vals, xpos in [(pos_vals, 1), (ctrl_vals, 2)]:
        jitter = np.random.normal(xpos, 0.04, size=len(vals))
        ax.scatter(jitter, vals, color="black", s=18, zorder=3, alpha=0.7)
    ax.set_title(label)
plt.suptitle("PRISM independent validation: ICE-REFERENCE (Li et al. 2018 M3 + LCROSS) vs CONTROL (checked-negative) sites\nSouth-pole sites only, n=%d tested (2 north-pole sites excluded, no PRISM coverage)" % len(tested))
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "validation_comparison.png"), dpi=150)
plt.close(fig)
print("wrote validation_comparison.png")
