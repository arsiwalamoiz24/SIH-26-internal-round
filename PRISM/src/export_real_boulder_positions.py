"""
Real per-boulder positions for rover-path obstacle avoidance.

Every prior boulder-detection pass in this project (src/boulder_detection_
shadowcam.py) only ever saved aggregate counts/mask-areas, never per-boulder
coordinates -- there was nothing to route a path around. This script reruns
the exact same trained model (PRISM/models/boulder_detector_yolov8n_seg.pt)
on the same local, already-downloaded, geolocated ShadowCam crop GeoTIFFs,
and additionally extracts each detection's real pixel bounding box, converts
it to real-world south-polar-stereographic meters via the crop's own affine
transform (rasterio), then to meters relative to the candidate's own center
-- the same coordinate convention as the PSR boundary / elevation grids --
so real boulder positions can be used directly as pathfinding obstacles.

No formula/model change from the original detection pass; this only adds
coordinate extraction on top of the same inference call.
"""

import json
import os

import numpy as np
import rasterio
from PIL import Image
from pyproj import Transformer
from ultralytics import YOLO

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(REPO, "PRISM", "models", "boulder_detector_yolov8n_seg.pt")
OUT_DIR = os.path.join(REPO, "frontend2", "public", "assets", "prism", "pathfinding")
os.makedirs(OUT_DIR, exist_ok=True)

NODATA_SENTINEL = -1e30
CONF_THRESHOLD = 0.1
MOON_RADIUS = 1737400
SOUTH_STEREO = f"+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +R={MOON_RADIUS} +units=m +no_defs"

CANDIDATES = {
    "SP_840980_0797630": (-84.098, 79.764, [
        os.path.join(REPO, "PRISM", "outputs", "objective_optical", "SP_840980_0797630_shadowcam_crop.tif"),
    ]),
    "SP_832640_0090770": (-83.264, 9.077, None),
    "SP_830080_0535120": (-83.008, 53.512, None),
    "SP_842420_0421060": (-84.242, 42.106, None),
    "SP_817950_1586580": (-81.795, 158.658, None),
    "SP_819860_1568660": (-81.986, 156.866, None),
    "SP_809570_2454450": (-80.957, 245.445, None),
}

SHORTLIST_DIR = os.path.join(REPO, "PRISM", "outputs", "objective_optical", "shortlist_shadowcam")


def percentile_stretch_to_rgb(data, nodata=NODATA_SENTINEL, lo_pct=1, hi_pct=99):
    valid = data[data > nodata]
    if valid.size == 0:
        return None
    lo, hi = np.percentile(valid, [lo_pct, hi_pct])
    stretched = np.clip((data - lo) / (hi - lo + 1e-12), 0, 1)
    stretched[data <= nodata] = 0
    img8 = (stretched * 255).astype(np.uint8)
    return np.stack([img8, img8, img8], axis=-1)


def main():
    model = YOLO(MODEL_PATH)
    stereo_tf = Transformer.from_crs("+proj=longlat +R=1737400 +no_defs", SOUTH_STEREO, always_xy=True)

    for cid, (lat, lon, explicit_tifs) in CANDIDATES.items():
        tifs = explicit_tifs or sorted(
            os.path.join(SHORTLIST_DIR, f) for f in os.listdir(SHORTLIST_DIR) if f.startswith(cid) and f.endswith(".tif")
        )
        if not tifs:
            print(f"{cid}: no crop TIFs found, skipping")
            continue

        cx, cy = stereo_tf.transform(lon, lat)
        boulders = []

        for tif in tifs:
            with rasterio.open(tif) as ds:
                data = ds.read(1)
                transform = ds.transform
                crs = ds.crs

            rgb = percentile_stretch_to_rgb(data)
            if rgb is None:
                continue
            pil_img = Image.fromarray(rgb)

            preds = model.predict(pil_img, conf=CONF_THRESHOLD, iou=0.45, verbose=False)
            r = preds[0]
            if r.boxes is None or len(r.boxes) == 0:
                continue

            to_stereo = Transformer.from_crs(crs, SOUTH_STEREO, always_xy=True)
            for box, conf in zip(r.boxes.xyxy.tolist(), r.boxes.conf.tolist()):
                x1, y1, x2, y2 = box
                px_col, px_row = (x1 + x2) / 2, (y1 + y2) / 2
                # Pixel -> this file's own CRS (map units) -> south-polar-stereographic meters.
                mx, my = transform * (px_col, px_row)
                sx, sy = to_stereo.transform(mx, my)
                radius_m = max((x2 - x1), (y2 - y1)) / 2 * abs(transform.a)  # box half-size in real meters
                boulders.append({
                    "x": round(sx - cx, 2),
                    "y": round(sy - cy, 2),
                    "radius_m": round(float(radius_m), 2),
                    "confidence": round(float(conf), 3),
                })

        print(f"{cid}: {len(boulders)} real boulder detections from {len(tifs)} crop(s)")
        with open(os.path.join(OUT_DIR, f"{cid}_boulders.json"), "w") as f:
            json.dump({"candidate_id": cid, "confidence_threshold": CONF_THRESHOLD, "boulders": boulders}, f)

    print("\nDone.")


if __name__ == "__main__":
    main()
