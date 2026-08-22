# PRISM — Product Requirements Document v2

**Probabilistic Radar Ice & Surface Mission System** *Lunar South Polar Subsurface Ice Detection, Surface Hazard Characterization, Landing Site Selection, and Rover Traverse Planning*

|                  |                                                                                                      |
| ---------------- | ---------------------------------------------------------------------------------------------------- |
| **Doc type**     | Product Requirements Document (hackathon submission + demo build, phased toward full implementation) |
| **Prepared for** | Handoff to Stitch (UI/UX prototyping) and Manus.im (build execution)                                 |
| **Context**      | ISRO-affiliated hackathon — Chandrayaan-2 DFSAR ice detection challenge                              |
| **Status**       | Draft v2.0 — supersedes v1.1                                                                         |

---

## 1. Executive Summary

PRISM is an integrated lunar south-polar analysis and mission-planning system built around one continuous scientific and operational chain:

> **PRISM uses radar to probabilistically detect and characterize subsurface ice, uses imagery and terrain data to understand the hazards around it, uses those combined insights to identify a safe landing site, and then plans the rover's optimal traverse based on the mission's priorities.**

It is organized around four mission objectives — **Ice Detection & Characterization, Surface & Hazard Characterization, Landing Site Planning,** and **Rover Traverse Planning** — that feed into one another sequentially and are presented in the UI as one coherent workflow rather than four disconnected tools.

The system's differentiator, carried over unchanged from v1, is that it replaces binary decisions (ice/no-ice, safe/unsafe, this-path/that-path) with probability distributions and propagates uncertainty through every downstream step, so that every number the system presents — an ice probability, a volume estimate, a landing-site score, a rover path — comes with an explicit confidence behind it.

## 2. Problem Statement

Every existing submission to this challenge (and the "official" reference workflow) treats lunar ice detection as a **binary classification problem**: a pixel either is or isn't ice, decided by a hard threshold on Circular Polarization Ratio (CPR > 1), sometimes ANDed with Degree of Polarization (DOP < 0.13). This throws away information, because:

- CPR > 1 is also produced by rough, chaotic rocky terrain — not just ice. The threshold is statistical, not physical.
- DEM-derived slope/roughness is treated as ground truth when it carries its own resolution and interpolation uncertainty.
- Volume estimates are single numbers with no error bars, based on dielectric mixing assumptions borrowed from unrelated regions.
- Surface hazard assessment (craters, boulders, shadowed terrain) is typically handled separately from ice detection, if at all — so a "high ice probability" region may in practice be inaccessible or unsafe, and nothing in the workflow surfaces that conflict.
- Path planning optimizes for distance/safety only — never for "where is ice most likely, and how do we reduce our uncertainty about it."
- The workflow is static: it produces a map once and never updates it as new data (or a rover) provides more information.

**PRISM's core thesis (unchanged from v1):** replace every binary decision in the pipeline with a probability distribution, carry that uncertainty through every downstream step — detection → characterization → hazard assessment → landing site selection → rover path planning → volume estimate — and never present a number without the confidence behind it.

## 3. Product Vision & Core Thesis

PRISM should not merely identify potential ice. It should communicate probability, confidence, and uncertainty, and use that information to make downstream mission-planning decisions — from where to land to where to drive.

The product is framed around a single integrated workflow, not four unrelated dashboard pages:

```
Detect Ice
   ↓
Characterize Ice + Confidence + Uncertainty
   ↓
Characterize Surface & Hazards
   ↓
Identify Safe Landing Sites Near Scientifically Valuable Regions
   ↓
Plan Rover Traverse
   ↓
Estimate / Refine Scientific Value and Uncertainty

```

Each stage consumes the outputs of the stage(s) before it. A landing site is not just "safe terrain" — it is safe terrain *near high-probability ice*. A rover path is not just "short and safe" — it trades off safety, scientific value (ice discovery / uncertainty reduction), and power efficiency, and the user can steer that tradeoff live.

## 4. Users & Context

| User What they need from PRISM                          |                                                                                                                                                           |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Hackathon judges (primary demo audience)**            | A fast, visually clear, interactive way to see *why* a probabilistic, end-to-end approach beats a binary, single-purpose one. 2–5 minutes of attention.   |
| **ISRO scientists (secondary, if selected to advance)** | Defensible methodology, traceable ice-detection decisions, actionable outputs (landing site, rover paths, drill sites, volume estimate with uncertainty). |
| **Team (Manthan + teammates)**                          | A tool they can actually operate live without it breaking, built from real ISRO/NASA public data, inside the time budget.                                 |

This is a **demo/analysis tool**, not a consumer product. The UI should feel like scientific mission-analysis software — a mission-control instrument — not a marketing website or SaaS admin dashboard. Every requirement below, especially UI/UX (§11–14), should be read through that lens.

## 5. Four Mission Objectives

PRISM is organized around four major objectives. Each is a distinct scientific/analytical stage, and each is a distinct workspace in the UI (§13), but together they form one mission-planning chain.

### Objective 1 — Detection & Characterization of Subsurface Ice

Use Chandrayaan-2 DFSAR radar data to detect and characterize likely subsurface ice — not as a binary "ice / no ice" call, but as a **probabilistic characterization** of where ice is likely to exist and how confident the system is.

Covers: CPR, DOP, dual-frequency (L/S band) backscatter, physics-informed signal decomposition, Bayesian probability modeling, uncertainty/confidence, and depth-resolved volume estimation. Volume estimation is a downstream scientific output of this objective, not a separate top-level objective (see §5, Objective 1 vs. old v1 FR-5). Drill-site / information-gain recommendation is likewise treated as a supporting capability of this objective rather than a fifth mission objective.

### Objective 2 — Surface & Hazard Characterization

Use Chandrayaan-2 OHRC imagery and LOLA DEM-derived terrain information to characterize the surface around candidate ice regions — crater morphology, boulders, terrain hazards, shadowed regions, slope, roughness, and elevation.

This objective complements ice detection rather than existing independently. It answers: *there may be ice here, but is the surrounding terrain actually usable/safe?* OHRC is already listed as a required data source in the v1 PRD's data table, but v1 had no dedicated functional requirement built around it — this objective closes that gap using only the data source and terrain concepts (slope, roughness, shadow) already present in v1's FR-3 and FR-4.

### Objective 3 — Landing Site Planning

Use the outputs of Objectives 1 and 2 to identify and rank candidate landing sites, considering terrain safety, slope, roughness, hazards/boulders, proximity to promising ice regions, and ice probability. The system produces candidate landing sites and explains *why* each is recommended. This is distinct from rover traverse planning.

### Objective 4 — Rover Traverse Planning

Once a landing site has been selected, determine how the rover should traverse the region, trading off safety, ice-discovery/scientific value, and power/efficiency. The system presents alternative paths — **Safety-first, Discovery/Science-first, Balanced** — and the user can adjust priorities live and see the resulting trajectory change.

---

## 6. Data Sources & Inputs

Preserved from v1, reorganized by objective.

| Source Provides Priority Primary objective(s)                                    |                                                             |                                                                       |                                                                                         |
| -------------------------------------------------------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Chandrayaan-2 DFSAR (S1/S2 Stokes parameter products, south polar region \~87°S) | CPR, DOP, dual-frequency (L/S band) backscatter             | **Required**                                                          | Objective 1                                                                             |
| Chandrayaan-2 OHRC imagery                                                       | High-res optical, crater morphology, boulder identification | **Required**                                                          | Objective 2                                                                             |
| LOLA DEM (NASA LRO, \~20m/pixel)                                                 | Elevation → slope, roughness, shadow geometry               | **Required**                                                          | Objective 2 (primary); also feeds Objective 3 safety scoring and Objective 4 path costs |
| DIVINER thermal data (NASA LRO)                                                  | Max/min surface temperature history                         | Optional — enriches thermal prior, degrades gracefully if unavailable | Objective 1 (thermal prior in Bayesian fusion)                                          |

Data formats: HDF5 / GeoTIFF (DFSAR), GeoTIFF (DEM, OHRC). Pipeline loads via `rasterio` / `h5py` / `GDAL`. No additional datasets are introduced beyond what v1 already specifies.

---

## 7. Scientific / Processing Pipeline

The processing pipeline is unchanged in substance from v1, restructured under the four objectives it now serves:

```
Raw datasets (DFSAR, OHRC, LOLA DEM, DIVINER)
        ↓
Processing / scientific pipeline
  ├─ Stokes parameter extraction → CPR, DOP                        (Obj. 1)
  ├─ Cloude-Pottier-style signal decomposition                     (Obj. 1)
  ├─ Bayesian fusion → P(ice) raster + uncertainty                 (Obj. 1)
  ├─ Volume estimation (Maxwell-Garnett) + credible interval       (Obj. 1)
  ├─ Drill-site / information-gain ranking                        (Obj. 1, supporting)
  ├─ OHRC + DEM terrain/hazard layer generation                    (Obj. 2)
  ├─ Landing-site scoring                                          (Obj. 3)
  ├─ Pareto rover-path graph solver                                (Obj. 4)
  └─ Science Confidence Budget (cross-cutting composite score)     (all objectives)
        ↓
Data-access layer / defined data contract (§15)
        ↓
Frontend

```

**Key architectural rule (unchanged from v1):** the frontend never talks to raw data or the pipeline directly — it only calls data-access layer functions, one per required output. Phase 1 (§16) implements these functions against raw/sample data; Phase 2 re-implements the same functions against the real pipeline output, in the same shape, so the frontend requires no redesign.

## 8. Functional Requirements

Restructured around the four objectives. All acceptance criteria and the Phase 1/Phase 2 phasing note carry over unchanged in substance from v1 — only the grouping has changed.

> **Phasing note (unchanged from v1):** For Phase 1 (demo), the dashboard is fed **raw/sample data** for each FR below rather than a fully computed pipeline. Each FR's acceptance criteria describes what the *dashboard must display and how it must behave*, regardless of whether the value behind it is a sample/raw figure (Phase 1) or a fully computed one (Phase 2). Nothing in the UI should visibly change when Phase 2 swaps the data source in — see §16.

### FR-1 — Subsurface Ice Detection & Probabilistic Characterization (Objective 1)

- Compute per-pixel `P(ice | radar, morphology, thermal)` instead of a binary CPR > 1 classification.
- Inputs combined: CPR + DOP (radar), shadow depth/fraction (morphology), temperature proxy (thermal, if DIVINER available).
- Output: continuous probability raster (0.0–1.0), not a red/green mask.
- **Acceptance criteria:** map renders as a continuous probability scale (not a hard-edged binary mask) using the discrete stepped color scale from §12; a toggle exists to compare against the naive binary CPR>1 map side-by-side. *(Phase 1: rendered from raw/sample CPR/DOP data. Phase 2: same component, fed the computed Bayesian fusion output.)*

**FR-1a — Physics-Informed Signal Decomposition**

- Decompose radar backscatter into volume scattering (ice-indicative), surface scattering (roughness), and double-bounce (boulders) components — Cloude-Pottier decomposition or a simplified equivalent.
- Use the volume/surface scattering ratio as a physically-grounded ice indicator, feeding into the main FR-1 probability fusion.
- **Acceptance criteria:** a decomposition map exists showing which regions are volume-scattering-dominant. *(Phase 1: illustrative/sample decomposition output. Phase 2: same panel, fed real Cloude-Pottier decomposition results.)*

**FR-1b — Volume Estimation with Uncertainty**

- Use L-band vs. S-band backscatter ratio to infer depth distribution (near-surface vs. buried).
- Apply a dielectric mixing model (Maxwell-Garnett or equivalent) to solve for ice fraction.
- Report **mean ± credible interval**, never a bare point estimate.
- **Acceptance criteria:** UI displays a volume number with an explicit uncertainty range, and a slider lets the user vary the assumed ice-concentration input and watch the estimate update live. *(Phase 1: figure computed from raw/sample band-ratio data. Phase 2: same readout, fed the real Maxwell-Garnett-derived estimate.)*

**FR-1c — Drill Site / Sparse Sampling Recommendation** *(supporting capability, not a top-level objective)*

- Identify up to 5 locations that would maximize information gain about the ice map if ground-truthed (Bayesian experimental design or a reasonable simplified proxy).
- **Acceptance criteria:** 5 candidate sites marked on the map, each with a one-line rationale. *(Phase 1: sample-derived candidates. Phase 2: same list component, fed the real information-gain ranking.)*

### FR-2 — Surface & Hazard Characterization (Objective 2)

- Render OHRC high-resolution optical imagery over the candidate region, with crater morphology and boulder features visually identifiable.
- Derive terrain layers from the LOLA DEM: slope, roughness, elevation, and shadow geometry — the same terrain-derived quantities v1 already required as inputs to landing-site scoring (v1 FR-3) and rover path costs (v1 FR-4), now surfaced as their own explicit, viewable layer set rather than only consumed internally.
- Support overlaying the Objective 1 ice-probability raster on top of the terrain/hazard layers, so the user can directly compare "where ice is likely" against "what the terrain around it looks like."
- **Acceptance criteria:** OHRC imagery and at least slope, roughness, and shadow layers render as togglable map overlays; the ice-probability raster can be shown as an overlay on the same view. *(Phase 1: rendered from raw/sample OHRC + DEM data. Phase 2: same component, fed real terrain-derived layers.)*

### FR-3 — Landing Site Selection (Objective 3)

- Score candidate sites outside the shadowed crater on: slope safety (<15°), proximity to high-P(ice) zones, and sunlight-hours availability (power) — unchanged from v1.
- Present each candidate with a visible scoring breakdown / rationale rather than a bare rank.
- **Acceptance criteria:** top landing site is highlighted on the terrain view with its scoring breakdown visible; multiple candidate sites are comparable side by side. *(Phase 1: raw/sample scoring inputs. Phase 2: same panel, fed real slope/proximity/sunlight scoring.)*

### FR-4 — Rover Traverse Planning (Objective 4)

- Generate rover paths on a cost graph where edges are weighted by slope penalty, P(ice) reward, and shadow/power penalty — not distance alone.
- Present at least three paths representing different tradeoff points: Safety-first, Discovery/Science-first, Balanced.
- Provide interactive priority controls (the three Pareto sliders, unchanged from v1) that move a point along the Pareto front and update the highlighted path in real time.
- **Acceptance criteria:** three distinct, labeled paths render on the terrain/map view; adjusting priority sliders visibly changes which path is highlighted. *(Phase 1: paths generated from raw/sample terrain costs. Phase 2: same panel and slider behavior, fed the real Pareto path solver.)*

---

## 9. Cross-Cutting Capabilities

These are not owned by a single objective — they are surfaced throughout the system.

### Science Confidence Budget

A single composite 0–100 score summarizing: data quality, algorithm agreement, cross-instrument corroboration, and uncertainty width. Displayed prominently as a gauge/dial, visible from the Mission Overview and re-contextualized within each objective workspace (e.g., an ice-specific confidence view within Objective 1). *(Phase 1: score computed from raw/sample inputs. Phase 2: same gauge, fed the real composite score.)*

### Uncertainty propagation

Every probabilistic or scored output in the system — ice probability, volume estimate, landing-site score, rover-path cost — must carry its uncertainty/confidence alongside it, not as a bare number. This is the connective tissue that makes the four objectives feel like one system rather than four tools: uncertainty computed in Objective 1 visibly informs the landing-site rationale in Objective 3 and the path costs in Objective 4.

## 10. System Workflow

The end-to-end workflow, unchanged in spirit from v1's five mission tasks but now explicit as the backbone of the whole product:

```
Detect Ice  →  Characterize Ice + Confidence + Uncertainty  →  Characterize Surface & Hazards
   →  Identify Safe Landing Sites Near Scientifically Valuable Regions
   →  Plan Rover Traverse  →  Estimate / Refine Scientific Value and Uncertainty

```

This is one integrated chain, not four unrelated dashboard pages. Every workspace in the UI (§13) is a detailed view *into* one stage of this chain, and the Mission Overview (§12) is the one screen that shows the whole chain at a glance.

## 11. UI/UX & Information Architecture

The v1 UI direction was a generic three-panel mission-control dashboard containing all functionality at once. That **visual language is preserved** — light theme, professional scientific/research-instrument aesthetic, high information density with clean hierarchy, technical typography, restrained colors, stepped-hue probability visualization — but the **structure** changes: the dashboard is no longer one page trying to hold every feature. It becomes five screens reflecting the four objectives plus one overview, so the product reads as one coherent story — **Detect → Characterize → Land → Traverse** — rather than a single overloaded page or four disconnected tools.

### Visual direction (carried over from v1, unchanged)

- **Light theme.** Clean, professional, scientific-instrument look — closer to a NASA/ISRO mission analytics tool or a data-science research dashboard than a "generated app." Avoid dark space/sci-fi styling, glow effects, neon accents, or anything reading as AI-generated boilerplate.
- White/near-white background, restrained neutral grays for structure (cards, panels, dividers). Probability data uses a **stepped, single-hue color scale** (5–6 discrete shade bands, light → dark for low → high) rather than a smooth multi-color gradient — a deliberate cartographic/choropleth choice. No decorative gradients anywhere in the interface.
- Typography: a clean technical sans (e.g., Inter, IBM Plex Sans) for UI chrome; a monospace font reserved for numeric readouts (coordinates, volume figures, confidence scores) to signal precision.
- Deliberate, custom layout choices (asymmetric panel widths, real grid alignment, considered spacing) rather than default component-library spacing.

### What changes: structure, not skin

- The existing Stitch-generated dashboard becomes the **Mission Overview / Mission Control landing screen** (§12), not a container for every feature.
- Do not simply expand the current dashboard by adding more cards. Instead, keep the visual design language and restructure the product around the four objective workspaces (§13), each reached from the Mission Overview.
- The earlier dark-themed HTML prototype (if referenced anywhere) is not a target UI and should not be preserved — layout, dark theme, navigation, component arrangement, and hardcoded values from that prototype are explicitly out of scope.

### Information architecture

| Screen Role                                     |                                                                                            |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Mission Overview                                | High-level summary of the whole workflow (Ice → Surface → Landing → Rover), landing screen |
| Objective 1 — Ice Detection & Characterization  | Detailed scientific workspace                                                              |
| Objective 2 — Surface & Hazard Characterization | Detailed scientific workspace                                                              |
| Objective 3 — Landing Site Planning             | Detailed decision workspace                                                                |
| Objective 4 — Rover Traverse Planning           | Detailed decision workspace                                                                |

This is not a normal SaaS website. It should feel like scientific mission-analysis software / mission-control instrument software, and a judge should be able to follow the scientific story quickly (see §14).

## 12. Mission Overview

A high-level summary of the entire mission analysis, allowing the user to understand the full workflow — **Ice → Surface → Landing → Rover** — quickly, without loading every detailed chart.

Should show:

- Main terrain/probability visualization (the 3D DEM-derived terrain with the ice-probability overlay, carried over from v1's Panel 1)
- Overall Science Confidence Budget
- Key ice findings (headline probability/volume figures)
- Surface/hazard summary
- Recommended landing site
- Rover-path summary
- Volume estimate (mean ± uncertainty)
- Major mission metrics

It should **not** become overloaded with every detailed chart — those live in the objective workspaces (§13), reached from here.

## 13. Objective Workspaces

### Objective 1 — Ice Detection & Characterization

Carries forward the core of v1's Panel 2 (Science Dashboard). Detailed workspace for: DFSAR data, CPR, DOP, Bayesian P(ice), binary-CPR-vs-Bayesian side-by-side comparison (the single most important visual in the demo, per v1 §7.2 — still true here), uncertainty, confidence, depth-resolved crater cross-section, volume estimation with credible interval, and drill-site/information-gain recommendations. This should be one of the strongest scientific views in the product.

### Objective 2 — Surface & Hazard Characterization

New workspace (§8, FR-2). Detailed workspace for: OHRC imagery, terrain visualization, boulder/hazard identification, slope, roughness, shadow, elevation — with the ice-probability raster overlayable for direct comparison. The user should be able to understand the relationship between "where is the ice?" and "what does the terrain around it look like?"

### Objective 3 — Landing Site Planning

Detailed workspace for: candidate landing sites, site scoring, safety, slope, roughness, hazards, proximity to high-probability ice, relevant scientific value, side-by-side site comparison, and recommendation/ranking. Candidate sites are displayed directly on the map, each accompanied by concise reasoning (carried over from v1 FR-3's scoring breakdown).

### Objective 4 — Rover Traverse Planning

Carries forward v1's Panel 3 (Mission Control) content. Detailed workspace for: the selected landing site, terrain constraints, ice probability, the three rover paths (Safety-first / Discovery-first / Balanced), power/efficiency, the three interactive Pareto sliders, path metrics, and the "Simulate Mission" animation (rover moving along the chosen path, "collecting observations," probability map subtly updating) — the signature demo moment from v1, unchanged in intent.

## 14. Interactions & Demo Flow

### Core interactions (carried over and extended from v1 §7.3)

1. Toggle between binary CPR map and Bayesian probability map (Objective 1).
2. Overlay the ice-probability raster on terrain/hazard layers (Objective 2).
3. Select/compare candidate landing sites (Objective 3).
4. Drag the three Pareto sliders → rover path updates (Objective 4).
5. Drag the ice-concentration slider → volume estimate + uncertainty bar updates (Objective 1).
6. Click "Simulate Mission" → animated rover traversal plays (Objective 4).
7. Hover/click a drill-site marker → shows its one-line rationale (Objective 1).

### Intended demo narrative

The judge should be able to follow one continuous story, screen by screen:

| Step Question Answered by  |                                            |                                                              |
| -------------------------- | ------------------------------------------ | ------------------------------------------------------------ |
| 1                          | Where is the ice?                          | DFSAR + Bayesian probability map (Objective 1)               |
| 2                          | How confident are we?                      | Confidence + uncertainty + supporting evidence (Objective 1) |
| 3                          | What does the terrain around it look like? | OHRC + terrain/hazard layers (Objective 2)                   |
| 4                          | Where can we safely land?                  | Landing-site candidates and ranking (Objective 3)            |
| 5                          | Once we land, where should the rover go?   | Alternative rover trajectories (Objective 4)                 |
| 6                          | What if we prioritize safety vs. science?  | Adjust controls → trajectory changes (Objective 4)           |

This workflow is central to the UX — every screen should reinforce which step of this chain the user is looking at.

### Explicitly out of scope for UI/UX (unchanged from v1)

- No account system, no settings persistence beyond the session.
- No mobile layout — demo is presented on a single large screen/projector.
- No error states beyond basic "data still loading" indicators.
- Animation should be slight — smooth transitions and one signature simulate-mission sequence, not a heavy motion-design pass.

## 15. Data Contracts / Frontend Architecture

**Frontend should not directly depend on raw scientific data (unchanged architectural principle from v1):**

```
Raw datasets
   ↓
Processing / scientific pipeline
   ↓
Data-access layer / defined data contract
   ↓
Frontend

```

The same contracts support Phase 1 (raw/sample data) and Phase 2 (real computed pipeline output) without redesigning the UI. At minimum, the frontend must eventually be able to receive structured outputs for:

| Output Feeds                                                |                                                      |
| ----------------------------------------------------------- | ---------------------------------------------------- |
| Ice probability raster                                      | Mission Overview, Objective 1, Objective 2 (overlay) |
| Decomposition map (volume/surface/double-bounce scattering) | Objective 1                                          |
| Terrain/hazard layers (slope, roughness, shadow, elevation) | Objective 2, Objective 3, Objective 4                |
| Candidate landing sites (with scoring breakdown)            | Objective 3, Mission Overview                        |
| Rover path geometries (safety / discovery / balanced)       | Objective 4, Mission Overview                        |
| Confidence metrics (Science Confidence Budget)              | All screens                                          |
| Volume estimate + uncertainty interval                      | Objective 1, Mission Overview                        |
| Drill / information-gain sites                              | Objective 1                                          |

Data-access functions (naming carried over from v1's §8, extended for the new objective structure): `getIceProbabilityMap()`, `getDecompositionMap()`, `getTerrainHazardLayers()`, `getLandingSites()`, `getRoverPaths()`, `getVolumeEstimate()`, `getDrillSites()`, `getConfidenceBudget()`. No more detailed API surface is specified here than is necessary to express the architecture — exact field names/types remain an open item (§21) to finalize before Stitch/Manus.im start.

**Key architectural rule (unchanged):** the frontend never talks to raw data or the pipeline directly — it only calls the data-access layer. Phase 1 implements these functions against raw/sample data; Phase 2 re-implements the same functions against real pipeline output, in the same shape. The component tree requires no changes between phases.

## 16. Phase 1 vs Phase 2

Two-phase philosophy carried over from v1, revised around the new four-objective scope.

| **Phase 1 — Hackathon Demo (now)** **Phase 2 — Full Implementation (post-demo)**  |                                                                                                                     |                                                                                      |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **What's built**                                                                  | Five screens (Mission Overview + 4 objective workspaces)                                                            | Same five screens, unchanged                                                         |
| **Data behind it**                                                                | Raw / sample DFSAR, OHRC, DEM, and derived values (static or lightly pre-processed)                                 | Live output of the full computed pipeline (§7)                                       |
| **Figures/panels shown**                                                          | The exact same panels, charts, gauges, and layout defined in §11–14                                                 | The exact same panels, charts, gauges, and layout — swapped to real computed figures |
| **Goal**                                                                          | Build a compelling, interactive dashboard demonstrating the four-objective workflow using available raw/sample data | Prove the same UX now reflects genuinely computed science                            |

**Phase 1 priorities (in order):**

1. Ice probability visualization (Objective 1)
2. Surface/hazard visualization (Objective 2)
3. Landing-site selection (Objective 3)
4. At least one interactive rover-path planning workflow (Objective 4)

**Why this matters for design (unchanged from v1):** because Phase 2 must be a drop-in data swap and not a redesign, no screen can be built as a one-off demo skin around hardcoded numbers. Every panel, chart, and readout must be built as a component that reads from the defined data contract (§15), currently fed by raw/sample values, later fed by the real pipeline.

## 17. Implementation Priorities / Tiers

Reworked from v1's Tier 1/2/3 to reflect the new four-objective scope. Time-boxed for a 30-hour build; each tier is independently demoable if time runs out.

| Priority Scope Includes  |                                                      |                                                                                                                                                                                                 |
| ------------------------ | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MUST-HAVE**            | Core interactive workflow across all four objectives | Bayesian ice probability map (Objective 1); terrain/surface visualization (Objective 2); at least one landing-site recommendation (Objective 3); at least one rover path (Objective 4)          |
| **SHOULD-HAVE**          | Scientific depth                                     | Confidence/uncertainty display; depth-resolved characterization; volume estimate with credible interval; hazard layers; multiple landing-site candidates; full three-path Pareto rover planning |
| **STRETCH**              | Differentiation from Tier-1-only teams               | Drill-site / information-gain optimization; "Simulate Mission" animation polish; richer terrain/hazard layering; additional data-layer overlays                                                 |

Suggested hour blocks (carried over from v1, still applicable): 0–4 data loading, 4–8 decomposition, 8–14 Bayesian probability map, 14–20 surface/hazard + landing site, 20–26 rover path + volume/drill sites, 26–30 dashboard polish + deck.

## 18. Non-Goals

Explicitly out of scope for this build (unchanged from v1):

- No physical rover hardware or real-time telemetry — this is a **pre-mission planning and analysis tool**, not flight software.
- No production-grade authentication, multi-user accounts, or persistence layer beyond what's needed for the demo session.
- No mobile-responsive design required — demo is presented on a single large screen/projector.
- Not attempting full radiative-transfer-grade EM simulation — simplified/approximate physics is acceptable if clearly labeled as such.
- Volume estimation and drill-site recommendation are not treated as standalone mission objectives (see §5) — they remain supporting outputs of Objective 1.

## 19. Success Criteria

Carried over from v1's success metrics, applied across the four-objective structure:

- A functioning interactive dashboard (Mission Overview + 4 objective workspaces) that judges can operate live.
- A Bayesian ice-probability map generated from real Chandrayaan-2 DFSAR data for the target PSR/doubly-shadowed crater region.
- At least one OHRC/terrain-derived hazard visualization overlaid with ice probability.
- At least one ranked landing-site recommendation with visible rationale.
- At least one Pareto-style rover path visualization (safety vs. ice-discovery vs. power tradeoff).
- A volume estimate reported as **mean ± uncertainty**, not a bare number.
- A shareable Google Drive link to the deployed dashboard, attached alongside the PPT submission.
- Judges/reviewers can, within the first 30 seconds of the demo, articulate the one-line differentiator (§Appendix).

## 20. Deliverables

**Phase 1 (hackathon):**

1. Filled hackathon PPT (10-slide template) describing the PRISM approach, using this PRD's language for consistency.
2. Deployed interactive dashboard (Mission Overview + 4 objective workspaces), running against raw/sample data (hosted; shareable link).
3. Google Drive link containing the dashboard link + any supporting notebooks/outputs, attached to the submission.
4. This PRD, as the shared reference for design (Stitch) and build (Manus.im) work.

**Phase 2 (post-demo, if the project continues):** 5. The same five screens, with each data-access function (§15) re-implemented against the real computed pipeline instead of raw/sample data — no redesign, no new screens.

## 21. Open Questions / Dependencies

- [ ] Team member names/roles for the PPT team slide.
- [ ] Confirm exact target crater/region (Faustini, Shackleton, or other) to scope DFSAR/OHRC data pull.
- [ ] Confirm DIVINER coverage availability for the chosen region (thermal prior degrades gracefully if absent — see FR-1).
- [ ] Confirm hosting target for the deployed dashboard (Vercel, Replit, etc.) before the Manus.im build starts, so the Drive link is ready ahead of the submission deadline.
- [ ] Decide how much of the physics decomposition (FR-1a) is genuinely implemented vs. simplified/approximated for time — should be stated honestly in the PPT regardless.
- [ ] Finalize the exact data shape (field names/types) for each data-access function in §15 before Stitch/Manus.im start, so Phase 1's sample data and Phase 2's real pipeline output are guaranteed to match without touching the frontend.
- [ ] Decide, if asked live by judges, how transparently to describe that Phase 1's figures come from raw/sample data rather than the finished pipeline.
- [ ] Confirm the exact terrain/hazard layer set for Objective 2 (which combination of slope/roughness/shadow/elevation is shown by default vs. toggled).

## 22. Stitch / Frontend Handoff

### Visual language

- Light scientific-instrument aesthetic
- Professional, research-oriented
- High information density with clean hierarchy
- No excessive neon/glow, no gradients
- Large-screen presentation (single projector/monitor, not responsive)
- Scientific visualization prioritized over decorative UI

### Core screens/workspaces

1. Mission Overview
2. Ice Detection & Characterization (Objective 1)
3. Surface & Hazard Characterization (Objective 2)
4. Landing Site Planning (Objective 3)
5. Rover Traverse Planning (Objective 4)

### Important interactions

- Bayesian vs. binary ice-map comparison (single most important visual)
- Map layer switching (OHRC, slope, roughness, shadow, ice-probability overlay)
- Selecting/comparing candidate landing sites
- Safety / Discovery / Efficiency priority controls
- Dynamic rover-path updates driven by those controls
- "Simulate Mission" animation

### Design principle

The UI should tell a coherent story — **Detect → Characterize → Land → Traverse** — rather than feeling like disconnected dashboards. Every screen should make clear which stage of that chain it represents and what feeds into it from the stage before.

---

## What Changed from PRD v1

| Area v1 v2                |                                                                                                         |                                                                                                                                                                                  |
| ------------------------- | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Framing                   | "Bayesian ice probability map + mission planning dashboard"                                             | Integrated four-objective mission-planning system                                                                                                                                |
| Structure                 | Five underlying mission tasks folded into FR-1…FR-7 on one dashboard                                    | Four explicit mission objectives, each with its own workspace                                                                                                                    |
| Surface/hazard analysis   | Implicit — OHRC listed as a required data source but no dedicated FR                                    | New, explicit Objective 2 / FR-2, built from OHRC + DEM data already in scope                                                                                                    |
| Volume estimation         | v1 FR-5, presented as a peer to the other FRs                                                           | Now FR-1b, explicitly a downstream output of Objective 1 — not a fifth objective                                                                                                 |
| Drill-site recommendation | v1 FR-6, presented as a peer to the other FRs                                                           | Now FR-1c, explicitly a supporting capability of Objective 1 — not a fifth objective                                                                                             |
| UI layout                 | Single three-panel dashboard (Terrain View / Science Dashboard / Mission Control) containing everything | Mission Overview landing screen + four dedicated objective workspaces; v1's three panels map roughly onto Overview, Objective 1, and Objective 4 respectively                    |
| Visual design language    | Light scientific-instrument aesthetic                                                                   | **Unchanged** — explicitly preserved, only the information architecture around it changes                                                                                        |
| Data architecture         | Data-access layer, Phase 1/Phase 2 split                                                                | **Unchanged in principle** — extended with two new functions (`getTerrainHazardLayers()`, and landing sites/rover paths renamed to plural to reflect multi-candidate comparison) |
| Demo narrative            | Implicit in the three-panel interaction list                                                            | Made explicit as a six-step Q&A narrative (§14) mapped directly to the four objectives                                                                                           |
| Tiers                     | Tier 1/2/3 by FR grouping                                                                               | MUST/SHOULD/STRETCH reorganized so every tier includes at least a thin slice of all four objectives                                                                              |

---

## Appendix: One-line pitch (for reference across all materials)

> "Every other team told you where the ice is. We told you how confident we are — and what to do next if we're wrong."