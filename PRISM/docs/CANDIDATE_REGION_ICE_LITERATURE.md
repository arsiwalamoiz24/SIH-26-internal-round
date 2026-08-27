# CANDIDATE_REGION_ICE_LITERATURE — published ice evidence for PRISM's 7 shortlisted PSRs

**Date:** 2026-08-27. **Purpose:** for each of PRISM's 7 shortlisted candidate
PSRs, identify the named crater / region it physically sits in, and list the
peer-reviewed literature reporting **water-ice or cold-trap evidence for that
same location** — so PRISM's radar/physics screening can be checked against
independent published evidence *at the same place*, not against "there is ice
on the Moon somewhere" reasoning.

**Method:** candidate coordinates from
`outputs/objective1/evidence_score/physics_evidence_score.json`. Named-crater
centres from the IAU Gazetteer of Planetary Nomenclature. Distances computed
this session (spherical, R = 1737.4 km, 30.29 km/° lat). Literature via
WebSearch/WebFetch, August 2026. Access status noted where a full-text fetch
was not obtained.

**This document does NOT overturn
[`LUNAR_SOUTH_POLE_ICE_VALIDATION_LITERATURE.md`](LUNAR_SOUTH_POLE_ICE_VALIDATION_LITERATURE.md)
(2026-08-26).** It refines one point that document under-stated: the primary
candidate is **inside Amundsen crater**, not "~15 km from" a separate nearby
site — and Amundsen has a real, if contested, published ice / cold-trap
record. The other six candidates' situation is unchanged: no location-specific
ice-detection paper exists for any of them.

---

## Summary table

| # | PSR ID | Lat, Lon (°E) | Sits in / nearest named crater | Location-specific ice literature | Evidence class |
|---|---|---|---|---|---|
| 1 (primary) | `SP_840980_0797630` | −84.098, 79.764 | **Inside Amundsen crater** (~15 km NW of centre; D≈103 km) | Sefton-Nash 2019; Qiao 2019; Fisher 2017; Hayne 2015; Schörghofer 2021 — **and** Li 2018 (negative), Brown 2022 (positive) | **Contested direct + strong cold-trap** |
| 5 | `SP_842420_0421060` | −84.242, 42.106 | NW rim of **Nobile crater** (~43 km from centre) | VIPER mission rationale; Reach 2023; Mons Mouton / Nobile Rim PSR characterisation (LPSC 2025) | Regional orbital-H + plausibility |
| 7 | `SP_830080_0535120` | −83.008, 53.512 | Inside **Scott crater** (~47 km from centre, D≈108 km); ~69 km N of Nobile | Same Nobile/Scott/VIPER corridor literature as #5 | Regional orbital-H + plausibility |
| 2 | `SP_832640_0090770` | −83.264, 9.077 | ~51 km N of **Malapert crater**, Mons Malapert / SPA-rim plateau | Basilevsky 2019; Kring 2025 (cold-trap modelling, not detection); Reach 2023 | Plausibility only |
| 3 | `SP_809570_2454450` | −80.957, 245.445 (−114.6) | At the rim of **Ashbrook crater** (far side, adjacent to Drygalski) | None location-specific | Latitude-band only |
| 4 | `SP_819860_1568660` | −81.986, 156.866 | **Amundsen–Ganswindt basin** interior; ~82 km NW of Wiechert | A–G basin exploration papers (volatiles discussed generically); none PSR-specific | Latitude-band only |
| 6 | `SP_817950_1586580` | −81.795, 158.658 | Amundsen–Ganswindt basin interior (~2 km from #4's region) | Same as #4 | Latitude-band only |

**Bottom line:** exactly **one** of the seven (the primary candidate) lies inside
a named crater with its own published water-ice / cold-trap literature
(**Amundsen**). That literature is genuinely mixed — multiple positive
cold-trap / LOLA-albedo / UV-frost results, one explicit M3 spectral
non-detection. Two more (#5, #7) lie in the **Nobile–Scott corridor that is
NASA VIPER's entire target rationale**, but no confirmed ice *detection* paper
exists for those specific PSRs — only the orbital hydrogen / neutron data that
motivated sending a rover there. The remaining four have no location-specific
ice paper at all.

---

## 1. `SP_840980_0797630` (primary) — inside Amundsen crater

**Geometry:** candidate centroid −84.098°, 79.764°E. Amundsen centre −84.5°,
82.8°E, D ≈ 103 km (r ≈ 51 km). Offset ≈ **15.4 km NW of the crater centre** —
firmly on the interior floor, in the northwestern quadrant. Amundsen's
well-studied permanently shadowed cold trap is on its **northern / north-western
floor and inner wall**, i.e. the same quadrant the candidate falls in. (Exact
overlap of the candidate's PSR polygon with the specific sub-regions in each
paper below was not verified pixel-by-pixel — treat as "same crater, same
general quadrant," not "same polygon.")

### Positive / supportive literature

- **Sefton-Nash, E. et al. (2019).** *"Evidence for ultra-cold traps and surface
  water ice in the lunar south polar crater Amundsen."* **Icarus 332, 1–13.**
  DOI 10.1016/j.icarus.2018.12.016. — Title says it directly. LOLA 1064-nm
  albedo, Diviner temperature, and LAMP far-UV in Amundsen's north-floor PSR
  are spatially correlated in the way expected for surface water ice; also
  identifies doubly-shadowed *ultra*-cold traps (~10–15 K colder than
  surroundings, up to ~40% areal fraction of the <112 K cold trap).
  *Access: abstract + secondary summaries only (ScienceDirect/ADS blocked).*
- **Qiao, L. et al. (2019).** *"Analyses of LOLA 1,064-nm Albedo in PSRs of
  Polar Crater Flat Floors…"* **Earth and Space Science 6, 1129–1149.** DOI
  10.1029/2019EA000567. — PSRs on flat crater floors (Amundsen among the
  worked examples) are systematically **brighter at 1064 nm** than adjacent
  sunlit terrain; the reflectance step coincides with the Diviner ~110 K
  contour; best explained by surface water ice. *Access: abstract + summary.*
- **Fisher, E. A. et al. (2017).** *"Evidence for surface water ice in the
  lunar polar regions."* **Icarus 292, 74–85.** DOI
  10.1016/j.icarus.2017.03.023. — LOLA reflectance rises sharply where Diviner
  T_max < ~110 K, co-located with LAMP; Amundsen's floor is among the
  south-polar sites showing this signature. *Access: secondary summary.*
- **Hayne, P. O. et al. (2015).** *"Evidence for exposed water ice in the
  Moon's south polar regions from LRO UV albedo and temperature measurements."*
  **Icarus 255, 58–69.** DOI 10.1016/j.icarus.2015.03.032. — LAMP off/on-band
  UV ratio + Diviner: patchy surface frost (few % areal) in the coldest PSRs,
  Amundsen included. *Access: secondary summary.*
- **Schörghofer, N. et al. (2021).** *"Carbon dioxide cold traps on the Moon."*
  **Geophysical Research Letters 48, e2021GL095533.** — Amundsen hosts ≈ **82
  km² of CO₂ cold traps** (T < 60 K) — the second-largest concentration on the
  Moon. Not water ice, but an independent confirmation that Amundsen's floor
  reaches volatile-trapping temperatures. *Access: secondary summary.*
- **Brown et al. (2022), Icarus 377, 114874** — lists **Amundsen** on its
  "resource-rich" PSR set (hydrogen/frost co-location modelling).

### Negative / contradictory literature (must be shown alongside)

- **Li, S. et al. (2018), PNAS 115(36):8907–8912** — Amundsen is one of the
  **explicit M3 negative controls**: checked for the 1.3/1.5/2.0 µm ice
  absorption triplet, none found. This is the single most-cited south-polar
  surface-ice map and it does **not** place Amundsen among its ~7 positive
  craters.

**Net for #1:** Amundsen is a real, named, repeatedly-studied cold trap with
multiple positive water-ice *indicators* (LOLA albedo, UV, thermal) and one
prominent spectral *non-detection*. It is the only PRISM candidate for which
"validate against published ice evidence at the same location" is even
possible — and even here the published record is split.

---

## 2. `SP_842420_0421060` (#5) & `SP_830080_0535120` (#7) — Nobile–Scott corridor (VIPER region)

**Geometry:**
- #5 (−84.242°, 42.106°E): ≈ 44 km from the centre of **Nobile crater**
  (−85.28°, 53.27°E, D ≈ 79 km) — on/just beyond its north-western rim.
- #7 (−83.008°, 53.512°E): inside **Scott crater** (−81.9°, 45.3°E, D ≈ 108 km),
  ≈ 47 km from its centre, and ≈ 69 km due north of Nobile. Nobile "lies to the
  south of Scott, along the western rim of Amundsen."

This corridor is **NASA VIPER's landing region** (western Nobile) and contains
the **Artemis III "Nobile Rim 1 / Nobile Rim 2"** candidate landing regions.

### Literature

- **VIPER mission science rationale** (e.g. Colaprete et al., mission
  definition papers; NASA VIPER site-selection releases 2021–2022) — the
  region was selected *because* orbital neutron / hydrogen data (LEND, LPNS)
  and thermal modelling indicate near-surface water ice in the many
  500–800 m PSRs around Nobile. This is **motivating orbital evidence, not a
  confirmed detection** — confirming it in situ was the mission's purpose
  (VIPER was cancelled in 2024; no surface data exist).
- **Reach, W. T. et al. (2023).** *"The Distribution of Molecular Water in the
  Lunar South Polar Region based upon 6 µm Spectroscopic Imaging."* **PSJ 4,
  45.** DOI 10.3847/PSJ/acb69d. — SOFIA 6.1 µm molecular-water map of the
  south polar region (5 km resolution). Reports enhanced H₂O on **south-facing
  inner crater rims and PSRs**; overall wetter toward ≈ −7°E, drier toward
  +28°E. Nobile/Scott (≈ 42–54°E) sit in the intermediate/drier part of the
  gradient, but the "south-facing inner rim" enhancement mechanism applies to
  Nobile's and Scott's northern inner walls. *Access: arXiv 2302.10815
  available.*
- **Mons Mouton / Nobile Rim PSR characterisation** — e.g. *"The Permanently
  Shadowed Regions at the Mons Mouton Artemis III Candidate"* (LPSC 2025, abs.
  #2742) and related Artemis III geology papers: catalogue the PSRs in this
  corridor, report Diviner T_max well below 110 K (min ~66 K in one),
  i.e. thermally ice-capable — again plausibility, not detection.
- **Cannon & Britt (2020), Icarus 347, 113778** — the Ice Favorability Index
  map covers this region; not queried per-candidate here (a concrete
  follow-up: sample the published IFI raster at all 7 candidate centroids).

**Net for #5/#7:** strong *programmatic* interest (VIPER + Artemis III) driven
by orbital hydrogen data, plus a regional SOFIA water map — but **no
peer-reviewed ice *detection* specific to these two PSRs.**

---

## 3. `SP_832640_0090770` (#2) — Mons Malapert / SPA-rim plateau

**Geometry:** −83.264°, 9.077°E — ≈ 51 km north of **Malapert crater** centre
(−84.9°, 12.9°E), on the high plateau near **Mons Malapert** (an Artemis III
candidate region ~120 km from the pole).

### Literature

- **Basilevsky, A. T. et al. (2019).** *"Potential Lunar Base on Mons
  Malapert: Topographic, Geologic and Trafficability Considerations."** Solar
  System Research 53, 383–398** (and LPSC 2019 #1140). — Thermal modelling:
  many small craters on the Malapert massif ridge stay cold enough to trap
  water ice (and CO₂) in the top ~1 m of regolith, and locally on the surface.
- **Kring, D. A. et al. (2025).** *"Notional Geological Traverses… on Mons
  Malapert."* **JGR Planets, 10.1029/2024JE008905**; **Wueller et al. (2025)**,
  geologic history of the Mons Malapert / Mons Mouton regions (JGR Planets
  10.1029/2025JE009127) — exploration/geology framing; PSR cold traps
  mentioned as targets, no ice detection.
- **Reach et al. (2023)** — this longitude (≈ 9°E) is near the "wetter" end
  (≈ −7°E) of their 6 µm water gradient; suggestive, not location-specific.

**Net for #2:** cold-trap *modelling* says ice is plausible here; no detection
paper targets this PSR.

---

## 4. `SP_819860_1568660` (#4) & `SP_817950_1586580` (#6) — Amundsen–Ganswindt basin interior

**Geometry:** −81.99°/−81.80°, ≈ 157–159°E — inside the **Amundsen–Ganswindt
peak-ring basin** (~335 km, straddling the Artemis exploration zone). Nearest
named crater with any ice literature: **Wiechert** (−84.5°, 165°E), ≈ 82–90 km
south-east — and Wiechert is an **M3 negative control** (Li et al. 2018).

### Literature

- **"The Amundsen–Ganswindt basin: an overlooked lunar peak-ring basin with
  multiple exploration opportunities"** (Icarus 2025, S0019103525002660) and
  the earlier *"A–G Basin: Multiple Opportunities for the Endurance Rover"*
  (2023) — argue the basin's PSRs (incl. the Slater Plain region) preserve
  ancient volatiles and are worth sampling. Volatiles discussed **generically**
  for the basin; **no per-PSR ice measurement** for anything at 157–159°E.
- No M3, Mini-RF, DFSAR, LAMP, or LOLA-albedo ice result targets these two
  PSRs specifically.

**Net for #4/#6:** basin-scale exploration interest only; nearest studied
crater is ice-negative.

---

## 5. `SP_809570_2454450` (#3) — Ashbrook crater (far side)

**Geometry:** −80.957°, 245.445°E (−114.6°) — at the rim of **Ashbrook crater**
(−81.4°, −112.5°), adjacent to Drygalski, on the far-side flank of the SPA rim.

### Literature

- None location-specific. Ashbrook appears in global PSR catalogues
  (Mazarico et al. 2011; McGovern et al. 2013) as a permanently shadowed
  crater, but no targeted ice-detection or cold-trap study was found.
- Falls inside the ≥ 77°S latitude band of **McClanahan et al. (2024)**'s
  widespread-hydrogen-sequestration thermal/topographic model — regional
  plausibility, not detection.

**Net for #3:** latitude-band plausibility only; the least-studied of the seven.

---

## 6. Region-independent evidence that applies to all 7

These do **not** discriminate between our candidates and their neighbours
(too coarse, or model-based), but are the honest "supporting context" layer:

- **McClanahan, T. P. et al. (2024), PSJ** (arXiv:2303.03911) — Diviner + LOLA
  model: widespread H₂ sequestration in south-polar cold traps poleward of
  ≈ 77°S. All 7 candidates (−80.96° to −84.24°) are inside this zone.
- **Sanin, A. B. et al. (2017), Icarus 283, 20–30** — LEND: water-equivalent
  hydrogen rises poleward, ≈ 0.1–0.13 wt% within 2–10° of the pole. Footprint
  ≈ 10 km FWHM — coarser than any candidate PSR (3–7 km across); regional only.
- **Hayne, P. O. et al. (2026), Nature Astronomy** (s41550-026-02822-9) —
  exposed-ice fraction correlates with shadow *age*: quasi-continuous ice
  accumulation near the south pole for ≈ 1.5 Gyr; the oldest craters hold the
  most ice. Implies our candidates' ice potential scales with their (not yet
  measured here) surface age.
- **Cannon, K. M. & Britt, D. T. (2020), Icarus 347, 113778** — Ice
  Favorability Index. **Actionable next step:** sample the published IFI
  raster (`astrogeology.usgs.gov` → "Moon Ice Favorability Index South Pole")
  at all 7 candidate centroids and record the value per candidate — this is
  the closest thing to a per-candidate published "ice likelihood" number that
  exists, and PRISM has not yet done it.

---

## 7. What this means for PRISM's validation goal

- **You cannot do a clean "our physics vs. published ice detection" match for
  6 of 7 candidates** — no paper reports ice (or reports its absence) for those
  specific PSRs. This is the same conclusion as the 2026-08-26 literature doc.
- **For the primary candidate you can, and should** — it is inside Amundsen.
  The check is not "does PRISM agree that Amundsen has ice" (the published
  record itself doesn't agree with itself); it is: **does PRISM's Amundsen-
  interior signature resemble PRISM's signature at the M3-positive craters
  (Faustini, Haworth, Shoemaker…) more than at the M3-negative craters
  (Wiechert, Hedervari…)?** That test already exists —
  [`INDEPENDENT_ICE_VALIDATION.md`](INDEPENDENT_ICE_VALIDATION.md) — and it
  came back null. Adding an explicit Amundsen-interior run (PRISM's full
  Pv/CPR/SERD/T-Ratio + DOP pipeline on the candidate's own polygon, compared
  against the Sefton-Nash/Qiao north-floor PSR footprint) is the single
  highest-value follow-up.
- **The Nobile–Scott pair (#5, #7) is the second-best target**: run PRISM's
  pipeline there and compare against the VIPER-region orbital-hydrogen
  expectation and the Reach 2023 6 µm map, understanding that neither is a
  confirmed detection.
- **Do not present any of this as "PRISM's candidates are near known ice
  sites"** — the honest phrasing is: *one candidate is inside a named,
  much-studied cold-trap crater with a split ice record; two more are in the
  region NASA judged promising enough to send VIPER; the other four have only
  latitude-band plausibility.*

---

**PDF corpus:** open-access / repository copies of most of the papers below are
saved in [`literature/`](literature/) — see [`literature/README.md`](literature/README.md)
for the manifest and manual-download links for the paywalled remainder.

## 8. References (this pass)

1. Sefton-Nash, E. et al. (2019). *Icarus* 332, 1–13. DOI 10.1016/j.icarus.2019.06.002.
2. Qiao, L. et al. (2019). *Earth and Space Science* 6, 1129–1149. DOI 10.1029/2019EA000567.
3. Fisher, E. A. et al. (2017). *Icarus* 292, 74–85. DOI 10.1016/j.icarus.2017.03.023.
4. Hayne, P. O. et al. (2015). *Icarus* 255, 58–69. DOI 10.1016/j.icarus.2015.03.032.
5. Schörghofer, N. et al. (2021). *GRL* 48, e2021GL095533. DOI 10.1029/2021GL095533.
6. Li, S. et al. (2018). *PNAS* 115(36), 8907–8912. DOI 10.1073/pnas.1802345115. *(Amundsen negative)*
7. Brown, R. H. et al. (2022). *Icarus* 377, 114874. DOI 10.1016/j.icarus.2021.114874.
8. Reach, W. T. et al. (2023). *PSJ* 4, 45. DOI 10.3847/PSJ/acb69d. arXiv:2302.10815.
9. Basilevsky, A. T. et al. (2019). *Solar System Research* 53, 383–398 (LPSC 2019 #1140).
10. Kring, D. A. et al. (2025). *JGR Planets*. DOI 10.1029/2024JE008905.
11. Wueller et al. (2025). *JGR Planets*. DOI 10.1029/2025JE009127.
12. "The Amundsen–Ganswindt basin…" (2025). *Icarus*. S0019103525002660.
13. McClanahan, T. P. et al. (2024). *PSJ*. arXiv:2303.03911.
14. Sanin, A. B. et al. (2017). *Icarus* 283, 20–30. DOI 10.1016/j.icarus.2016.10.019.
15. Hayne, P. O. et al. (2026). *Nature Astronomy*. DOI 10.1038/s41550-026-02822-9.
16. Cannon, K. M. & Britt, D. T. (2020). *Icarus* 347, 113778. DOI 10.1016/j.icarus.2020.113778.
17. Sinha, R. K. et al. (2026). *npj Space Exploration* 2, 22 — studied doubly-shadowed craters **inside Faustini/Haworth/Shoemaker only** (F2, F3, H3, S1 positive); **no overlap with any PRISM candidate**.

**Access caveat:** items 1–5, 7, 9–12 were read via abstracts + cross-checked
secondary summaries only (ScienceDirect / AGU / ADS returned bot walls to
direct fetches this session). Titles, authors, years, journals, and DOIs are
high-confidence; specific in-text numbers attributed to them should be
verified against the primary PDF before being quoted in a PRISM deliverable.
