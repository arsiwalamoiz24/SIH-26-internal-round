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
| Frontend setup | [`frontend/README.md`](./frontend/README.md) |

## Layout

```
PRISM/            science pipeline: src/ (pipelines), notebooks/, outputs/ (results),
                   docs/ (topic docs), data/ (small real reference data, tracked)
frontend/          Next.js dashboard (Mission Control UI)
data/              large raw satellite data -- gitignored, not committed
scripts/           legacy/ = utility scripts (tracked), local_only/ = contains
                   API credentials, gitignored, never commit
DECISIONS.md        why things are the way they are -- read this first if confused
PROJECT_GUIDE.md    full project explainer
PRISM_PRD.md        requirements
```

## Modules

1. **Ice Detection** (`PRISM/src/radar_pipeline.py`, `ml_*_pipeline.py`) — DFSAR Pv/CPR/SERD/T-Ratio screening + Isolation Forest. Real, done, documented in `PRISM/docs/ML_METHODS.md`.
2. **Hazard Mapping — terrain** (`PRISM/src/hazard_map_*.py`) — LOLA DEM slope/roughness/illumination. Real, done (primary candidate + full 7-shortlist + regional overview).
2b. **Hazard Mapping — optical** (`PRISM/src/cnn_yolo_interface.py`) — boulder detection via YOLOv8/CNN. Not built yet — blocked on finding an OHRC scene that covers the candidate; see `PRISM/docs/ML_METHODS.md` for where to look next.
3. **Landing Site Selection** — slope + solar + ice-proximity scoring. Illustrative model in the frontend today, not yet fed by the real Module 2 output above.
4. **Rover Traverse** — A* pathfinding. Same status as #3.
5/6. **Frontend** — `frontend/`, Next.js dashboard rendering all of the above.

## Quick facts
- Primary ice candidate: PSR `SP_840980_0797630`, −84.098°, 79.764°, area 14.234 km².
- Frontend: `cd frontend && npm install && npm run dev`.
- Python pipelines: `source venv/bin/activate` at repo root, then run any `PRISM/src/*.py` script directly.
