# Archived v0.9 Legacy Stack

**Archived:** Phase 1 migration (2026-06-15)

These modules were the pre-v2 AGI loop. They were **not imported** by the live
FastAPI app (`backend/app.py` → `src.chetnaos.orchestrator.runtime`).

## Contents

| Path | Role |
|------|------|
| `backend/agi/` | Recursive goal loop (`run_loop`) |
| `backend/chetna_core.py` | v1 conscious runtime kernel |
| `backend/memory.py` | `Smriti` SQLite store (separate `smriti` table) |
| `backend/dharma_net.py` | Keyword dharma filter |
| `backend/world_state.py` | Legacy world state dict |
| `backend/evolution_engine.py` | Stub evolution adapter |
| `workspace.py` | Orphaned in-memory workspace (superseded by `workspace_state.py`) |

## Live replacements

| Legacy | Live (v2) |
|--------|-----------|
| `backend/agi/loop.py` | `src/chetnaos/orchestrator/cognitive_cycle.py` |
| `Smriti` | `memory/db.py` + `organism/memory.py` |
| `DharmaFilter` | `constitution/` + `reflection/reflection_v2.py` |
| `WorldState` | `organism/world_model.py` |
| `workspace.py` | `organism/workspace_state.py` |

Do not import from this archive in production code.
