import os
import re
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone
from torch.serialization import add_safe_globals

import numpy as np
import requests
from PIL import Image

# Optional dependencies required only for the WorldStrat super-resolution stage.
# Install the WorldStrat environment/dependencies before running:
# https://github.com/worldstrat/worldstrat
import torch
from torch.serialization import add_safe_globals

# HighResNet will be imported later after WORLDSTRAT_REPO is set
# CONFIG
# ---------------------------------------------------------------------

# IMPORTANT:
# Do NOT hard-code your Copernicus credentials in source code.
# Export them before running:
#   export COPERNICUS_CLIENT_ID="..."
#   export COPERNICUS_CLIENT_SECRET="..."
CLIENT_ID = "sh-74626b13-18e8-40f8-af09-c98a7eda7c5a"
CLIENT_SECRET = "DUE0rGsXXn3Q3y7xeqOzNG3JsMtlr2Hz"

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError(
        "Missing COPERNICUS_CLIENT_ID / COPERNICUS_CLIENT_SECRET environment variables."
    )

WORLDSTRAT_REPO = os.environ.get("WORLDSTRAT_REPO")
if WORLDSTRAT_REPO:
    sys.path.insert(0, WORLDSTRAT_REPO)

# Now we can safely import HighResNet and add to safe globals
from src.modules import HighResNet
add_safe_globals([HighResNet])

OUT_DIR = Path("/Users/moiz/.gemini/antigravity-ide/brain/b822b698-3f2b-48b1-826a-9869d4208bfe/")  # Convert to Path object

# WorldStrat model/checkpoint. Download once if it is not present.
WORLDSTRAT_CHECKPOINT = Path(os.environ.get(
    "WORLDSTRAT_CHECKPOINT",
    OUT_DIR / "worldstrat_model.ckpt"  # This now works because OUT_DIR is a Path object
))
WORLDSTRAT_CHECKPOINT_URL = (
    "https://raw.githubusercontent.com/worldstrat/worldstrat/main/"
    "pretrained_model/model.ckpt"
)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# Number of temporal revisits expected by the released WorldStrat model.
# The released checkpoint was trained with 8 Sentinel-2 L2A revisits.
NUM_REVISITS = 8

# We keep your original large RGB view.
DISPLAY_SIZE = 512

# WorldStrat's released checkpoint is designed around a 50x50 LR chip
# (10 m pixels = ~500 m) and produces a 500x500 SR output.
SR_LR_SIZE = 50
SR_OUTPUT_SIZE = 500

# The released WorldStrat checkpoint is trained with a 50x50 LR chip
# (10 m pixels = ~500 m) and a 500x500 HR output. The notebook's
# input_size=160 is the larger training context; the actual inference
# tensor shown in the notebook is 8x12x50x50.
SR_CONTEXT_SIZE = 50

# Centers near (79.35227, 33.39848)
centers = [
    (79.35227, 33.39848),  # Original
    (79.36500, 33.40500),  # Offset 1
    (79.34000, 33.39000),  # Offset 2
    (79.37500, 33.38500),  # Offset 3
    (79.36000, 33.41500),  # Offset 4
]

# Original ~3 km x 3 km boxes for the normal RGB outputs.
DISPLAY_HALF_SIZE_DEG = 0.0135

# The SR model consumes a 50x50 LR chip. At Sentinel-2's 10 m bands,
# this corresponds to roughly a 500 m x 500 m product.
# Keep the existing 3 km RGB view separately.
SR_HALF_SIZE_DEG = 0.00225

TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/"
    "protocol/openid-connect/token"
)
CATALOG_URL = "https://sh.dataspace.copernicus.eu/api/v1/catalog/1.0.0/search"
PROCESS_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"


# ---------------------------------------------------------------------
# SENTINEL-2 EVALSCRIPTS
# ---------------------------------------------------------------------

RGB_EVALSCRIPT = """
//VERSION=3
function setup() {
  return {
    input: ["B02", "B03", "B04", "dataMask"],
    output: { bands: 3, sampleType: "AUTO" }
  };
}

function evaluatePixel(sample) {
  if (sample.dataMask === 0) {
      return [0, 0, 0];
  }

  return [
    2.8 * sample.B04,
    2.8 * sample.B03,
    2.8 * sample.B02
  ];
}
"""

# WorldStrat uses all 12 Sentinel-2 bands. Sentinel Hub will resample the
# bands to the requested output grid. We request the grid at 10 m GSD.
# Band order is B01..B12, excluding B10 because Sentinel-2 L2A does not
# provide B10 surface reflectance.
ALL_12_BANDS_EVALSCRIPT = """
//VERSION=3
function setup() {
  return {
    input: [
      "B01", "B02", "B03", "B04",
      "B05", "B06", "B07", "B08",
      "B8A", "B09", "B11", "B12",
      "dataMask"
    ],
    output: {
      bands: 12,
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {
  if (sample.dataMask === 0) {
    return [
      0,0,0,0,0,0,0,0,0,0,0,0
    ];
  }

  return [
    sample.B01, sample.B02, sample.B03, sample.B04,
    sample.B05, sample.B06, sample.B07, sample.B08,
    sample.B8A, sample.B09, sample.B11, sample.B12
  ];
}
"""


# ---------------------------------------------------------------------
# COPERNICUS AUTH
# ---------------------------------------------------------------------

def get_token():
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["access_token"]


# ---------------------------------------------------------------------
# CATALOG
# ---------------------------------------------------------------------

def search_sentinel_features(token, bbox, start_date, end_date, limit=100):
    payload = {
        "bbox": bbox,
        "datetime": (
            f"{start_date.strftime('%Y-%m-%dT00:00:00Z')}/"
            f"{end_date.strftime('%Y-%m-%dT23:59:59Z')}"
        ),
        "collections": ["sentinel-2-l2a"],
        "limit": limit,
    }

    response = requests.post(
        CATALOG_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    response.raise_for_status()

    return response.json().get("features", [])


def parse_sentinel_datetime(dt_string):
    """
    Parse an ISO-8601 datetime string from the Sentinel Hub catalog API.

    Python 3.9's datetime.fromisoformat() only accepts fractional seconds
    with exactly 3 or 6 digits (this was relaxed in Python 3.11). Sentinel
    Hub sometimes returns other lengths (e.g. ".34" or ".3421"), which
    raises ValueError: Invalid isoformat string. We normalize the fractional
    part to 6 digits (microseconds) before parsing.
    """
    s = dt_string.replace("Z", "+00:00")

    def _pad_fraction(match):
        frac = match.group(1)[:6].ljust(6, "0")
        return f".{frac}"

    s = re.sub(r"\.(\d+)", _pad_fraction, s)
    return datetime.fromisoformat(s)


def select_temporal_revisits(features, n=NUM_REVISITS, max_cloud=60.0):
    """
    Select up to n observations distributed through time rather than simply
    taking the globally clearest scenes.

    This is important for the SR model: it needs multiple temporally matched
    observations, not eight copies of the same cloud-free date.
    """

    cleaned = []

    for feature in features:
        props = feature.get("properties", {})
        dt_string = props.get("datetime")

        if not dt_string:
            continue

        cloud = props.get("eo:cloud_cover", 100)
        try:
            cloud = float(cloud)
        except (TypeError, ValueError):
            cloud = 100.0

        if cloud <= max_cloud:
            dt = parse_sentinel_datetime(dt_string)
            cleaned.append((dt, cloud, feature))

    # Newest first.
    cleaned.sort(key=lambda x: x[0], reverse=True)

    if not cleaned:
        return []

    # Greedily select observations separated by at least ~4 days.
    selected = []
    for candidate in cleaned:
        if all(abs((candidate[0] - x[0]).days) >= 4 for x in selected):
            selected.append(candidate)
        if len(selected) == n:
            break

    # If the spacing constraint left us short, fill with remaining best dates.
    if len(selected) < n:
        selected_ids = {id(x[2]) for x in selected}
        for candidate in cleaned:
            if id(candidate[2]) not in selected_ids:
                selected.append(candidate)
            if len(selected) == n:
                break

    selected.sort(key=lambda x: x[0])
    return selected


# ---------------------------------------------------------------------
# SENTINEL HUB PROCESS API
# ---------------------------------------------------------------------

def process_image(token, bbox, dt, evalscript, width, height, fmt):
    payload = {
        "input": {
            "bounds": {
                "properties": {
                    "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
                },
                "bbox": bbox,
            },
            "data": [
                {
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "timeRange": {
                            "from": dt,
                            "to": dt,
                        }
                    },
                }
            ],
        },
        "output": {
            "width": width,
            "height": height,
            "responses": [
                {
                    "identifier": "default",
                    "format": {"type": fmt},
                }
            ],
        },
        "evalscript": evalscript,
    }

    response = requests.post(
        PROCESS_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "image/tiff" if fmt == "image/tiff" else "image/jpeg",
        },
        json=payload,
        timeout=180,
    )

    response.raise_for_status()
    return response.content


def save_rgb_jpeg(content, path):
    path.write_bytes(content)


def decode_float32_tiff(content, width, height, bands=12):
    """
    Decode Sentinel Hub's FLOAT32 TIFF response.

    Rasterio is preferred because it preserves TIFF band structure.
    """
    import rasterio
    from rasterio.io import MemoryFile

    with MemoryFile(content) as memfile:
        with memfile.open() as dataset:
            arr = dataset.read()

    expected = (bands, height, width)
    if arr.shape != expected:
        raise RuntimeError(
            f"Unexpected TIFF shape {arr.shape}; expected {expected}."
        )

    return arr.astype(np.float32)


# ---------------------------------------------------------------------
# WORLDSTRAT
# ---------------------------------------------------------------------

def download_worldstrat_checkpoint():
    if WORLDSTRAT_CHECKPOINT.exists():
        return

    print("Downloading WorldStrat pretrained checkpoint...")
    response = requests.get(WORLDSTRAT_CHECKPOINT_URL, timeout=300)
    response.raise_for_status()

    WORLDSTRAT_CHECKPOINT.write_bytes(response.content)
    print(f"Saved checkpoint to {WORLDSTRAT_CHECKPOINT}")


# Modify the load_worldstrat_model function
def load_worldstrat_model():
    from src.lightning_modules import LitModel

    # PyTorch >=2.6 defaults torch.load to weights_only=True, which only
    # unpickles a small allowlist of "safe" types. The WorldStrat checkpoint
    # references several custom classes (HighResNet, DoubleConv2d, etc.), and
    # the installed pytorch_lightning version calls torch.load() internally
    # without forwarding weights_only, so add_safe_globals() alone can't fix
    # it (and triggers an unrelated AttributeError in some PL versions).
    #
    # We force weights_only=False for this one load. This re-enables full
    # pickle deserialization, which is only safe because we downloaded this
    # checkpoint ourselves from the official WorldStrat repo.
    _original_torch_load = torch.load

    def _weights_only_false_load(*args, **kwargs):
        kwargs["weights_only"] = False
        return _original_torch_load(*args, **kwargs)

    torch.load = _weights_only_false_load
    try:
        model = LitModel.load_from_checkpoint(
            checkpoint_path=str(WORLDSTRAT_CHECKPOINT),
            map_location=DEVICE,
        )
    finally:
        torch.load = _original_torch_load

    model.to(DEVICE)

    # The checkpoint's submodules (e.g. kornia's Resize) were restored via
    # unpickling, which sets an object's __dict__ directly and skips
    # __init__(). Newer kornia versions added internal attributes like
    # `_disable_features` to their base Module class that only get set in
    # __init__ — so unpickled instances from an older kornia are missing
    # them, causing AttributeError the first time the module is called.
    # Patch any missing attributes back in after load, rather than pinning
    # to an old kornia (which risks breaking compatibility with the current
    # torch/pytorch_lightning versions instead).
    _kornia_module_defaults = {
        "_disable_features": False,
    }
    patched = 0
    for module in model.modules():
        for attr, default in _kornia_module_defaults.items():
            if "kornia" in type(module).__module__ and not hasattr(module, attr):
                object.__setattr__(module, attr, default)
                patched += 1
    if patched:
        print(f"Patched {patched} missing kornia module attribute(s) after checkpoint load.")

    return model

def prepare_worldstrat_input(revisits):
    """
    revisits:
        list of arrays shaped [12, H, W], with H=W=160.

    Returns:
        Tensor [1, 8, 12, 160, 160].
    """
    if len(revisits) != NUM_REVISITS:
        raise ValueError(
            f"WorldStrat checkpoint expects {NUM_REVISITS} revisits; "
            f"got {len(revisits)}."
        )

    x = np.stack(revisits, axis=0).astype(np.float32)

    # Sentinel-2 L2A reflectance is typically returned by Sentinel Hub in
    # reflectance units. WorldStrat normalizes its LR inputs. The exact
    # published constants are available in src.datasources.py.
    #
    # We import them rather than hard-coding guessed values.
    from src.datasources import JIF_S2_MEAN, JIF_S2_STD

    mean = np.asarray(JIF_S2_MEAN, dtype=np.float32).reshape(1, 12, 1, 1)
    std = np.asarray(JIF_S2_STD, dtype=np.float32).reshape(1, 12, 1, 1)

    # WorldStrat's preprocessing expects normalized LR imagery.
    x = (x - mean) / std

    tensor = torch.from_numpy(x).unsqueeze(0)
    return tensor


@torch.inference_mode()
def run_worldstrat(model, revisits):
    x = prepare_worldstrat_input(revisits).to(DEVICE)

    y_hat = model(x)

    # Released model returns [B, 1, C, H, W].
    if y_hat.ndim == 5:
        y_hat = y_hat[:, 0]

    return y_hat.detach().cpu().numpy()[0]


def make_rgb_from_sr(sr):
    """
    Convert WorldStrat output to an RGB JPEG.

    The released checkpoint may output either 3 bands (already RGB) or 12 bands
    (full multispectral). Handle both cases gracefully.

    If 12-band: WorldStrat band order is B01,B02,B03,B04,...
    True colour = B04 (idx 3), B03 (idx 2), B02 (idx 1).
    If 3-band: already RGB order.
    """
    if sr.shape[0] >= 4:
        rgb = sr[[3, 2, 1]]
    else:
        # 3-band output — use as-is (model outputs RGB directly)
        rgb = sr[:3]

    # Robust per-channel percentile stretch for visualization only.
    output = np.zeros_like(rgb, dtype=np.float32)

    for c in range(3):
        channel = rgb[c]
        lo, hi = np.nanpercentile(channel, [2, 98])

        if hi <= lo:
            output[c] = 0
        else:
            output[c] = np.clip((channel - lo) / (hi - lo), 0, 1)

    output = (np.moveaxis(output, 0, -1) * 255).astype(np.uint8)
    return Image.fromarray(output, mode="RGB")


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main():
    token = get_token()
    print(f"Using device: {DEVICE}")

    # The import path for WorldStrat should point to a local clone of the
    # repository. For example:
    #
    #   git clone https://github.com/worldstrat/worldstrat
    #   export PYTHONPATH="/path/to/worldstrat:$PYTHONPATH"
    #
    # We download only the checkpoint here.
    download_worldstrat_checkpoint()
    model = load_worldstrat_model()

    today = datetime.now(timezone.utc).date()
    # Use a recent temporal window. The released WorldStrat model expects 8
    # revisits; we choose the best temporally distributed observations within
    # this window rather than pretending there is exactly one scene every week.
    LOOKBACK_DAYS = int(os.environ.get("SR_LOOKBACK_DAYS", "120"))
    start_date = today - timedelta(days=LOOKBACK_DAYS)

    display_bboxes = [
        [
            lon - DISPLAY_HALF_SIZE_DEG,
            lat - DISPLAY_HALF_SIZE_DEG,
            lon + DISPLAY_HALF_SIZE_DEG,
            lat + DISPLAY_HALF_SIZE_DEG,
        ]
        for lon, lat in centers
    ]

    sr_bboxes = [
        [
            lon - SR_HALF_SIZE_DEG,
            lat - SR_HALF_SIZE_DEG,
            lon + SR_HALF_SIZE_DEG,
            lat + SR_HALF_SIZE_DEG,
        ]
        for lon, lat in centers
    ]

    for i, (display_bbox, sr_bbox) in enumerate(
        zip(display_bboxes, sr_bboxes), start=1
    ):
        print(f"\n========== REGION {i} ==========")

        # -------------------------------------------------------------
        # 1. Find temporal Sentinel-2 observations
        # -------------------------------------------------------------
        features = search_sentinel_features(
            token,
            sr_bbox,
            start_date,
            today,
            limit=100,
        )

        revisits = select_temporal_revisits(features, NUM_REVISITS)

        if not revisits:
            print(f"Region {i}: no usable Sentinel-2 scenes found at all; skipping.")
            continue

        print("Selected Sentinel-2 revisits:")
        for j, (dt_obj, cloud, feature) in enumerate(revisits, start=1):
            print(f"  {j}: {dt_obj.isoformat()} | cloud={cloud:.1f}%")

        # -------------------------------------------------------------
        # 2. Preserve your existing 3 km RGB image
        # This always runs, even if there aren't enough revisits for SR.
        # -------------------------------------------------------------
        latest_dt = revisits[-1][0].isoformat().replace("+00:00", "Z")

        print(f"Fetching latest RGB image: {latest_dt}")

        rgb_content = process_image(
            token=token,
            bbox=display_bbox,
            dt=latest_dt,
            evalscript=RGB_EVALSCRIPT,
            width=DISPLAY_SIZE,
            height=DISPLAY_SIZE,
            fmt="image/jpeg",
        )

        rgb_path = OUT_DIR / f"zoom_img_{i}.jpg"
        save_rgb_jpeg(rgb_content, rgb_path)
        print(f"Saved {rgb_path}")

        # -------------------------------------------------------------
        # WorldStrat SR needs exactly NUM_REVISITS temporally distributed
        # scenes. If we don't have enough, stop here for this region —
        # the plain RGB image above has already been saved regardless.
        # -------------------------------------------------------------
        if len(revisits) < NUM_REVISITS:
            print(
                f"Region {i}: only {len(revisits)} usable revisits found; "
                f"skipping WorldStrat SR because the released checkpoint "
                f"expects {NUM_REVISITS}. (Try raising SR_LOOKBACK_DAYS or "
                f"the max_cloud threshold if you need SR for this region.)"
            )
            continue

        # -------------------------------------------------------------
        # 3. Fetch 8 x 12-band Sentinel-2 temporal stack
        # -------------------------------------------------------------
        lr_revisits = []

        for j, (dt_obj, cloud, feature) in enumerate(revisits, start=1):
            dt = dt_obj.isoformat().replace("+00:00", "Z")

            print(
                f"Fetching SR input {j}/{NUM_REVISITS}: "
                f"{dt} | cloud={cloud:.1f}%"
            )

            tiff_content = process_image(
                token=token,
                bbox=sr_bbox,
                dt=dt,
                evalscript=ALL_12_BANDS_EVALSCRIPT,
                width=SR_CONTEXT_SIZE,
                height=SR_CONTEXT_SIZE,
                fmt="image/tiff",
            )

            arr = decode_float32_tiff(
                tiff_content,
                width=SR_CONTEXT_SIZE,
                height=SR_CONTEXT_SIZE,
                bands=12,
            )

            lr_revisits.append(arr)

            time.sleep(0.5)

        # Save the exact temporal stack used for SR.
        stack = np.stack(lr_revisits, axis=0)
        stack_path = OUT_DIR / f"region_{i}_sentinel2_8revisit_stack.npz"
        np.savez_compressed(
            stack_path,
            data=stack,
            dates=np.array(
                [x[0].isoformat() for x in revisits],
                dtype=object,
            ),
        )
        print(f"Saved temporal stack: {stack_path}")

        # -------------------------------------------------------------
        # 4. WorldStrat multi-frame super-resolution
        # -------------------------------------------------------------
        print("Running WorldStrat multi-frame super-resolution...")

        sr = run_worldstrat(model, lr_revisits)

        sr_npz_path = OUT_DIR / f"region_{i}_worldstrat_sr_12band.npz"
        np.savez_compressed(sr_npz_path, data=sr)
        print(f"Saved SR 12-band output: {sr_npz_path}")

        sr_rgb = make_rgb_from_sr(sr)
        sr_rgb_path = OUT_DIR / f"region_{i}_worldstrat_sr_rgb.jpg"
        sr_rgb.save(sr_rgb_path, quality=95)
        print(f"Saved SR RGB: {sr_rgb_path}")

        time.sleep(1)

    print("\nDone.")


if __name__ == "__main__":
    main()