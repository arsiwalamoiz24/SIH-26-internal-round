# PRISM

Lunar south-pole water-ice screening, hazard mapping, and landing/traverse planning, built on real Chandrayaan-2 DFSAR radar and NASA LOLA terrain data. Team OUTLIERs, SIH26_76.

## Start here

| If you want... | Read |
|---|---|
| The full plain-English explainer (problem, data, pipeline, glossary) | [`PROJECT_GUIDE.md`](./PROJECT_GUIDE.md) |
| **Why** things are built the way they are, and what changed recently | [`DECISIONS.md`](./DECISIONS.md) |
| The original requirements/spec | [`PRISM_PRD.md`](./PRISM_PRD.md) |
| Science pipeline status, module ownership, what's real vs. planned | [`PRISM/PROJECT_STATUS.md`](./PRISM/PROJECT_STATUS.md) |
| Topic-by-topic science documentation (DOP, physics results, validation, ML methods) | [`PRISM/docs/`](./PRISM/docs/) |
| Open questions / TODO | [`PRISM/TODO.md`](./PRISM/TODO.md) |
| Frontend setup | [`frontend2/README.md`](./frontend2/README.md) |
| What's current as of 2026-08-27 (ML status, traverse engine, frontend audit) | [`PRISM/docs/CURRENT_STATUS_2026-08-27.md`](./PRISM/docs/CURRENT_STATUS_2026-08-27.md) |
| Hackathon evaluation talk track + Q&A (supersedes `script.pdf`) | [`EVALUATION_SCRIPT.md`](./EVALUATION_SCRIPT.md) |

## Layout

```
PRISM/            science pipeline: src/ (pipelines), notebooks/, outputs/ (results),
                   docs/ (topic docs), data/ (small real reference data, tracked)
frontend2/         Next.js dashboard (current -- frontend/ is the old, dead one)
data/              large raw satellite data -- gitignored, not committed
scripts/           legacy/ = utility scripts (tracked), local_only/ = contains
                   API credentials, gitignored, never commit
DECISIONS.md        why things are the way they are -- read this first if confused
PROJECT_GUIDE.md    full project explainer
PRISM_PRD.md        requirements
```

## Modules

1. **Ice Detection** (`PRISM/src/radar_pipeline.py`, `ml_*_pipeline.py`) — DFSAR Pv/CPR/SERD/T-Ratio screening + Isolation Forest. Real, done, documented in `PRISM/docs/ML_METHODS.md`.
2. **Hazard Mapping — terrain** (`PRISM/src/hazard_map_*.py`) — LOLA DEM slope/roughness/illumination. Real, done (primary candidate + full 7-shortlist + regional overview + Faustini/Cabeus at their own real full extent).
2b. **Hazard Mapping — optical** (`PRISM/src/export_real_boulder_positions.py`, `shadowcam_featured_sites.py`) — real YOLOv8n-seg boulder detection on real ShadowCam imagery, now covering all 9 sites (7 screened candidates + Faustini + Cabeus).
3. **Landing Site Selection** — real slope/illumination/crater-boundary scoring with a real ~85m safe-radius clearance check (`frontend2/src/lib/traversePlanner.ts`), fed by real Module 2 hazard/elevation data.
4. **Rover Traverse** — real weighted A* with directional (switchback-aware) slope cost + a real battery state-of-charge model against a 14-day mission budget. Same file as #3.
5/6. **Frontend** — `frontend2/`, Next.js dashboard rendering all of the above.

## Quick facts
- Primary ice candidate: PSR `SP_840980_0797630`, −84.098°, 79.764°, area 14.234 km².
- Featured external-validation sites: Faustini (M3 spectral ice detection) and Cabeus (LCROSS direct water detection) — real external evidence, not PRISM-screened candidates; PRISM's own radar signal is reported honestly for both, not fabricated.
- Frontend: `cd frontend2 && npm install && npm run dev`.
- Python pipelines: `source venv/bin/activate` at repo root, then run any `PRISM/src/*.py` script directly.
