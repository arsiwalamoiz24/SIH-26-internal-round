# DIVINER_DATA_ACQUISITION — real Diviner Polar Resource Product, located and verified

**Date:** 2026-09-17. This document reports the real, live HTTP lookup
performed this session against the NASA PDS Geosciences Node — not a
citation, not a plan. The file itself is acquired by `src/acquire_diviner_prp.py`
(next step); this doc records where it comes from and how that was confirmed.

---

## 1. PDS product identifier

**`LRO-L-DLRE-4-RDR-V1`** — Diviner Lunar Radiometer Experiment, Level 4
Reduced Data Record, "Polar Resource Product" (PRP) tier. South-pole file:
`dlre_prp_south.tab`, bundle `lrodlr_1001`.

## 2. Archive location and URL resolution

Initial URL, found via web search of the PDS Geosciences Node's Diviner
product listing:
```
http://pds-geosciences.wustl.edu/lro/lro-l-dlre-4-rdr-v1/lrodlr_1001/data/prp/dlre_prp_south.tab
```

This URL is **not dead** but the PDS server has since reorganized its
directory structure to a URN-based path. A live `curl -sI -L` (HEAD
request, following redirects) against the HTTPS form of the above URL,
run this session, returned:

```
HTTP/1.1 302 Redirect
Location: https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_prp/dlre_prp_south.tab

HTTP/1.1 200 OK
Content-Length: 604800210
Content-Type: text/plain
Last-Modified: Thu, 22 Feb 2018 04:17:50 GMT
Accept-Ranges: bytes
```

**Canonical, confirmed-working URL (use this one):**
```
https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_prp/dlre_prp_south.tab
```

Public, **no login required** — confirmed by the anonymous `200 OK` above.
No authentication headers, cookies, or query tokens were needed. The
original (pre-redirect) URL also works, since the server transparently
redirects it — but the canonical URL is used directly to avoid the extra
round trip and because it's the address that will remain stable if the
legacy path is eventually removed.

## 3. File identity — verified without downloading

`Content-Length: 604800210` bytes, matching the expected file size
recorded from the prior session's work with this exact file
(`604,800,210` bytes / `2,880,000` mesh rows + 1 header row). This is a
strong identity check performed via `HEAD` request alone, before any
bytes were transferred — `Accept-Ranges: bytes` confirms the server also
supports resumable/partial downloads if ever needed.

`Last-Modified: Thu, 22 Feb 2018` — consistent with this being the
original, unmodified PDS archive product (Diviner PRP products were
released circa 2017–2018), not a re-processed or updated variant.

## 4. Row/column structure (from prior session's extraction, to be re-verified after download)

Fixed-width or CSV `.tab` file, 2,880,000 data rows (one per triangular
mesh element in the south-polar DEM), 15 columns including
`tri_clon` / `tri_clat` (triangle centroid longitude/latitude) and
`temp_max` (annual maximum bolometric surface temperature, Kelvin) — the
column PRISM's thermal gate uses. Exact byte/row verification is
performed programmatically by `acquire_diviner_prp.py`'s `verify()`
function after download, not assumed from this doc alone.

## 5. Destination

`<repo-root>/data/raw/diviner/dlre_prp_south.tab` — gitignored via the
existing root-level `/data/` rule (confirmed in `.gitignore`), matching
`src/radar_pipeline.py`'s own `REPO/data/raw/...` convention for large
raw satellite products. **Not** under `PRISM/data/`, which the repo's
actual `.gitignore` does not protect.

## 6. Download command (to be run via `acquire_diviner_prp.py`)

```bash
curl -L -o data/raw/diviner/dlre_prp_south.tab \
  "https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/data_derived_prp/dlre_prp_south.tab"
```
(`-L` required — the legacy URL 302-redirects; the canonical URL above
does not need it but `-L` is harmless either way.)

## 7. Verification result

**Deferred to `acquire_diviner_prp.py`'s `verify()` step** (byte count +
row count check against the file on disk after download). This doc
records the pre-download identity check (§3) only.
