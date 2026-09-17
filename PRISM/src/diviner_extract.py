"""Reusable Diviner Polar Resource Product (PRP) extraction module.

Consolidates the nearest-mesh-centroid haversine lookup that was
duplicated between src/pm4w_detector_v2.py's original one-off extraction
and src/pm4w_faustini_extension.py's real_diviner_temperature(). Neither
of those files is modified by this module -- this is an additive,
standalone Phase-2 consumer (PRISM_NEXT_PHASE_PLAN.md, "Supersedes
NOTHING").

See docs/DIVINER_DATA_ACQUISITION.md for where dlre_prp_south.tab comes
from and how its identity was confirmed before download.
"""
import os

import numpy as np
import pandas as pd

DIVINER_PRP_COLUMNS = [
    "tri1_x", "tri1_y", "tri1_z", "tri2_x", "tri2_y", "tri2_z",
    "tri3_x", "tri3_y", "tri3_z", "tri_clon", "tri_clat", "tri_calt",
    "temp_avg", "temp_max", "ice_depth",
]

MOON_RADIUS_KM = 1737.4
EXPECTED_BYTES = 604_800_210
EXPECTED_ROWS = 2_880_000

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DEST = os.path.join(REPO, "data", "raw", "diviner", "dlre_prp_south.tab")


def resolve_diviner_path(explicit_path=None) -> str:
    """explicit_path arg > DIVINER_PRP_PATH env var > default repo-root location."""
    if explicit_path:
        return explicit_path
    env_path = os.environ.get("DIVINER_PRP_PATH")
    if env_path:
        return env_path
    return DEFAULT_DEST


def load_diviner_prp(path=None, usecols=("tri_clon", "tri_clat", "temp_max")) -> pd.DataFrame:
    path = resolve_diviner_path(path)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Diviner PRP file not found at {path}. See "
            "docs/DIVINER_DATA_ACQUISITION.md for the confirmed download URL, "
            "and run `python src/acquire_diviner_prp.py` to fetch it. "
            "Never fabricates data in place of a missing file."
        )
    return pd.read_csv(
        path, skiprows=1, names=DIVINER_PRP_COLUMNS, usecols=list(usecols)
    )


def nearest_centroid_temperature(df, lat, lon, temp_col="temp_max") -> tuple:
    """Returns (temp_K, distance_km) to the nearest mesh-triangle centroid.

    Same haversine + lon<0 -> +360 normalization already proven correct
    across all 9 prior site lookups (<0.26 km each, pm4w_faustini_extension.py).
    """
    tlon = df["tri_clon"].to_numpy()
    tlat = df["tri_clat"].to_numpy()
    tlon_norm = np.where(tlon < 0, tlon + 360, tlon)
    lon_norm = lon + 360 if lon < 0 else lon

    dlat = np.radians(tlat - lat)
    dlon = np.radians(tlon_norm - lon_norm)
    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(np.radians(lat)) * np.cos(np.radians(tlat)) * np.sin(dlon / 2) ** 2
    )
    dist_km = 2 * MOON_RADIUS_KM * np.arcsin(np.sqrt(np.clip(a, 0, 1)))
    idx = np.argmin(dist_km)
    return float(df[temp_col].iloc[idx]), float(dist_km[idx])


def batch_lookup(df, sites: dict) -> dict:
    """sites: {site_key: {"lat": ..., "lon": ...}, ...}

    Loads df ONCE (caller passes it in), reuses across all sites -- fixes
    the prior per-site 600MB re-read. Returns
    {site_key: {"temp_max_K", "distance_km", "n_mesh_rows"}} or Nones if
    df is empty/unavailable for that lookup; caller maps None -> "NO_DATA",
    never a blank cell.
    """
    n_rows = len(df)
    results = {}
    for site_key, meta in sites.items():
        lat, lon = meta["lat"], meta["lon"]
        if n_rows == 0:
            results[site_key] = {"temp_max_K": None, "distance_km": None, "n_mesh_rows": n_rows}
            continue
        temp_k, dist_km = nearest_centroid_temperature(df, lat, lon)
        results[site_key] = {"temp_max_K": temp_k, "distance_km": dist_km, "n_mesh_rows": n_rows}
    return results
