"""
Tier 0 diagnostic: run the trained boulder detector (PRISM/models/
boulder_detector_yolov8n_seg.pt, YOLOv8n-seg, trained on BoulderNet real
lunar NAC imagery elsewhere on the Moon, validated box mAP50=0.551) on
this project's own real ShadowCam PSR crops for the first time.

This has never been done -- the model's own README explicitly says so.
This script does NOT claim a validated detection result: there is no
ground truth for boulders inside a permanently-shadowed crater anywhere
in existence, and the model was trained on sunlit imagery, a real domain
gap from these photon-starved crops. This is a diagnostic run to see
whether the model transfers at all, informing whether any image
enhancement (Tier 1/2) is worth building.

Preprocessing note: the float32 calibrated-radiance crops are percentile-
stretched (1st-99th of VALID pixels only) to 8-bit range so YOLO can
ingest them. This is plain dynamic-range mapping for viewability, not a
scientific enhancement claim -- kept clearly distinct from Tier 1/2's
labeled "enhancement" methods.
"""
import json
import os

import numpy as np
import rasterio
from PIL import Image
from ultralytics import YOLO

MODEL_PATH = "PRISM/models/boulder_detector_yolov8n_seg.pt"
OUT_DIR = "PRISM/outputs/objective_optical/boulder_detection"
CONF_THRESHOLDS = [0.05, 0.10, 0.25]
NODATA_SENTINEL = -1e30  # matches shortlist_shadowcam extraction convention


def find_crops():
    crops = ["PRISM/outputs/objective_optical/SP_840980_0797630_shadowcam_crop.tif"]
    shortlist_dir = "PRISM/outputs/objective_optical/shortlist_shadowcam"
    for f in sorted(os.listdir(shortlist_dir)):
        if f.endswith(".tif"):
            crops.append(os.path.join(shortlist_dir, f))
    return crops


def percentile_stretch_to_rgb(data, nodata=NODATA_SENTINEL, lo_pct=1, hi_pct=99):
    valid = data[data > nodata]
    if valid.size == 0:
        return None, {"n_valid": 0, "pct_valid": 0.0}
    lo, hi = np.percentile(valid, [lo_pct, hi_pct])
    stretched = np.clip((data - lo) / (hi - lo + 1e-12), 0, 1)
    stretched[data <= nodata] = 0
    img8 = (stretched * 255).astype(np.uint8)
    rgb = np.stack([img8, img8, img8], axis=-1)
    stats = {
        "n_valid": int(valid.size),
        "pct_valid": round(100 * valid.size / data.size, 2),
        "stretch_lo": float(lo),
        "stretch_hi": float(hi),
    }
    return rgb, stats


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUT_DIR, "raw_inference"), exist_ok=True)

    model = YOLO(MODEL_PATH)
    crops = find_crops()
    print(f"Found {len(crops)} real crops to process")

    results_summary = {}

    for crop_path in crops:
        crop_id = os.path.splitext(os.path.basename(crop_path))[0]
        with rasterio.open(crop_path) as ds:
            data = ds.read(1)

        rgb, stretch_stats = percentile_stretch_to_rgb(data)
        if rgb is None:
            print(f"{crop_id}: no valid pixels, skipping")
            results_summary[crop_id] = {"error": "no_valid_pixels"}
            continue

        pil_img = Image.fromarray(rgb)

        crop_results = {"preprocessing": "percentile_stretch_1_99", **stretch_stats, "by_conf_threshold": {}}

        for conf in CONF_THRESHOLDS:
            preds = model.predict(pil_img, conf=conf, iou=0.45, verbose=False)
            r = preds[0]
            n_det = len(r.boxes) if r.boxes is not None else 0
            confs = r.boxes.conf.tolist() if n_det > 0 else []
            mask_areas = []
            if r.masks is not None:
                for m in r.masks.data:
                    mask_areas.append(float(m.sum().item()))

            crop_results["by_conf_threshold"][str(conf)] = {
                "n_detections": n_det,
                "mean_conf": float(np.mean(confs)) if confs else None,
                "max_conf": float(np.max(confs)) if confs else None,
                "mask_areas_px": mask_areas,
            }

            if conf == 0.10:  # save one annotated visualization per crop at a representative threshold
                annotated = r.plot()
                out_png = os.path.join(OUT_DIR, "raw_inference", f"{crop_id}_conf{conf}.png")
                Image.fromarray(annotated[:, :, ::-1]).save(out_png)

        print(f"{crop_id}: pct_valid={stretch_stats['pct_valid']}%  "
              f"detections@0.05/0.10/0.25 = "
              f"{crop_results['by_conf_threshold']['0.05']['n_detections']}/"
              f"{crop_results['by_conf_threshold']['0.1']['n_detections']}/"
              f"{crop_results['by_conf_threshold']['0.25']['n_detections']}")

        results_summary[crop_id] = crop_results

    out = {
        "source_type": "DERIVED",
        "description": (
            "YOLOv8n-seg boulder detector (trained on BoulderNet sunlit LROC NAC "
            "imagery elsewhere on the Moon, validated mAP50 box=0.551, mask=0.179) "
            "run for the first time on this project's own real ShadowCam PSR crops. "
            "KNOWN DOMAIN GAP: training data is sunlit, this data is permanently-"
            "shadowed low-photon-count calibrated radiance. This is a diagnostic run, "
            "not a validated detection result -- no ground-truth boulders exist for "
            "any PSR interior to confirm against, anywhere. Preprocessing is a plain "
            "percentile stretch to 8-bit range for model ingestion, not a scientific "
            "enhancement claim."
        ),
        "model": MODEL_PATH,
        "conf_thresholds_tested": CONF_THRESHOLDS,
        "crops": results_summary,
    }
    out_path = os.path.join(OUT_DIR, "raw_inference_summary.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
