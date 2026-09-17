"""Idempotent downloader for the Diviner Polar Resource Product (south).

See docs/DIVINER_DATA_ACQUISITION.md for how this URL was located and
confirmed. Never guesses a URL if one isn't set.
"""
import argparse
import os
import sys
import urllib.request

from diviner_extract import EXPECTED_BYTES, EXPECTED_ROWS, resolve_diviner_path

DIVINER_PRP_URL = (
    "https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/"
    "data_derived_prp/dlre_prp_south.tab"
)


def download(url=None, dest=None, force=False) -> str:
    url = url or DIVINER_PRP_URL
    if not url:
        raise ValueError(
            "DIVINER_PRP_URL is unset — see docs/DIVINER_DATA_ACQUISITION.md "
            "for how to locate it. Refusing to guess a download URL."
        )
    dest = dest or resolve_diviner_path()

    if not force and os.path.exists(dest) and os.path.getsize(dest) == EXPECTED_BYTES:
        print(f"[skip] {dest} already matches expected size ({EXPECTED_BYTES} bytes)")
        return dest

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print(f"[download] {url}\n       -> {dest}")
    req = urllib.request.Request(url, headers={"User-Agent": "PRISM/thermal-gate"})
    with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
        total = int(resp.headers.get("Content-Length", 0))
        written = 0
        chunk_size = 1024 * 1024
        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            written += len(chunk)
            if total:
                pct = 100 * written / total
                print(f"\r  {written:,}/{total:,} bytes ({pct:.1f}%)", end="", flush=True)
        print()
    return dest


def verify(path) -> dict:
    if not os.path.exists(path):
        return {"bytes_ok": False, "rows_ok": False, "path": path, "error": "file not found"}

    size = os.path.getsize(path)
    bytes_ok = size == EXPECTED_BYTES

    with open(path, "r", encoding="ascii", errors="replace") as f:
        row_count = sum(1 for _ in f) - 1  # minus header row
    rows_ok = row_count == EXPECTED_ROWS

    return {
        "bytes_ok": bytes_ok,
        "rows_ok": rows_ok,
        "path": path,
        "actual_bytes": size,
        "expected_bytes": EXPECTED_BYTES,
        "actual_rows": row_count,
        "expected_rows": EXPECTED_ROWS,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=None, help="Override DIVINER_PRP_URL")
    parser.add_argument("--dest", default=None, help="Override download destination")
    parser.add_argument("--force", action="store_true", help="Re-download even if dest exists")
    args = parser.parse_args()

    path = download(url=args.url, dest=args.dest, force=args.force)
    result = verify(path)

    print(f"bytes_ok={result['bytes_ok']} rows_ok={result['rows_ok']}")
    if not (result["bytes_ok"] and result["rows_ok"]):
        print(f"VERIFICATION FAILED: {result}", file=sys.stderr)
        sys.exit(1)
    print(f"Verified: {path}")


if __name__ == "__main__":
    main()
