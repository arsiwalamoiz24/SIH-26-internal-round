"""
Real ShadowCam extraction for Faustini and Cabeus (the two featured
external-validation sites), reusing the exact same validated search +
windowed-crop + real-vs-noise-verification pipeline already proven for the
7 screened candidates (shadowcam_batch_verify.py) -- same real ASU/im-ldi
PDS archive search, true-polygon frame containment (not bbox), and
adjacent-pixel-correlation sanity check. No new method, just new coordinates.

Faustini and Cabeus were previously missing real ShadowCam imagery entirely
(that product was only ever extracted for the 7 candidates) -- this closes
that gap instead of reusing another site's photo.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shadowcam_batch_verify import find_covering_frames, get_cog_url, extract_and_verify

OUT_DIR = "PRISM/outputs/objective_optical/featured_shadowcam"

SITES = {
    "SP_871460_0840750": (-87.146, 84.075),                          # Faustini (catalog point)
    "SP_844580_3134320": (-84.45787607588048, -46.5676458422382),    # Cabeus (true PSR centroid)
}


def main():
    results = {}
    for cid, (lat, lon) in SITES.items():
        print(f"\n=== {cid} ({lat},{lon}) ===", flush=True)
        try:
            hits = find_covering_frames(lat, lon)
        except Exception as e:
            print("  search failed:", e, flush=True)
            results[cid] = {"error": str(e)}
            continue
        print(f"  {len(hits)} true-polygon-verified frames", flush=True)
        if not hits:
            results[cid] = {"n_frames": 0}
            continue

        picked = hits[:2]
        frame_results = []
        for r in picked:
            try:
                cog = get_cog_url(r["url"])
                if not cog:
                    print(f"  {r['identifier']}: no map_raw COG link found", flush=True)
                    continue
                out_tif = f"{OUT_DIR}/{cid}_{r['identifier']}.tif"
                stats = extract_and_verify(cog, lat, lon, 1500, out_tif)
                stats["identifier"] = r["identifier"]
                stats["incidence_angle"] = r["incidence_angle"]
                stats["resolution"] = r["resolution"]
                stats["cog_url"] = cog
                print(f"  {r['identifier']}: incidence={r['incidence_angle']} "
                      f"corr={stats['adjacent_pixel_correlation']:.3f} pct_valid={stats['pct_valid']}", flush=True)
                frame_results.append(stats)
            except Exception as e:
                print(f"  {r['identifier']}: FAILED {e}", flush=True)
        results[cid] = {"n_frames": len(hits), "extracted": frame_results}

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(f"{OUT_DIR}/summary.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nDONE")


if __name__ == "__main__":
    main()
