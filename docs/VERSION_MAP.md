# ChetnaOS Version Map

**Single source of truth** — last updated 2026-06-15  
**Active architecture:** ChetnaOS v3 (developmental cognitive organism)  
**Active cycle:** `src/chetnaos/cycle/cognitive_cycle.py` — 27 stages via `ExecutiveController`  
**Active memory hierarchy:** `Memory` → `WorkingMemory` → `MemoryHierarchy` → `memory/*.json` + `MemoryStore`

---

## Active Production Modules

| Layer | Canonical path | Role |
|-------|----------------|------|
| HTTP shell | `backend/app.py`, `backend/api/*` | FastAPI routes → single runtime |
| Runtime singleton | `backend/runtime.py` → `src/chetnaos/runtime/runtime.py` | One `CognitiveCycle` per process |
| Cognitive cycle | `src/chetnaos/cycle/cognitive_cycle.py` | Locked 27-stage pipeline |
| State machine | `src/chetnaos/runtime/state_machine.py` | Stage ordering |
| Sleep | `src/chetnaos/runtime/sleep_manager.py` | SLEEP → CONSOLIDATE → FORGET → WAKE |
| Executive | `src/chetnaos/cognition/executive.py` | Stage gating (26 wired + DECIDE) |
| Reasoning | `src/chetnaos/reasoning/reasoning.py` | Primary LLM call |
| Prompt assembly | `src/chetnaos/reasoning/prompt_builder.py` | Constitution + context |
| Context | `src/chetnaos/reasoning/context_builder.py` | Organ context packet |
| LLM router | `src/chetnaos/reasoning/llm_router.py` | Groq / stub |
| Memory store | `src/chetnaos/memory/store.py`, `memory_kernel/memory_item.py` | Normalized persistence |
| Working memory | `src/chetnaos/memory/working_memory.py` | Session WM |
| Beliefs | `src/chetnaos/organism/beliefs.py` | `memory/beliefs.json` |
| Belief revision | `src/chetnaos/cognition/belief_revision.py` | Gradual confidence updates |
| Agent tools | `src/chetnaos/tools/agent_tools.py` | calc / search |
| Frontend chat | `frontend/index.html` | Primary UI |
| Frontend dashboard | `frontend/dashboard.html` | Cognitive telemetry (existing) |
| Conversations | `backend/conversation_store.py` | Persistent chat (JSON) |
| UI session | `backend/workspace_store.py` | Refresh-safe workspace state |

### Organ implementations (logic lives in `organism/`)

All 28 frozen organs per `ARCHITECTURE_FREEZE.md`. Implementation: `src/chetnaos/organism/<name>.py`.  
Re-export shims only: `src/chetnaos/organs/<name>/__init__.py` — **do not import shims in new code**.

---

## Experimental / Observation-Only

| Module | Path | Status |
|--------|------|--------|
| Phase 8 Experiment 1 | `scripts/experiment_1_soak.py` | 100-cycle soak — observe only, no logic changes |
| Self-trainer goals | `src/chetnaos/organism/self_trainer.py` | Generates practice goals; not user-facing product |
| Kalpavriksha plugin | `backend/plugins/kalpavriksha/` | Separate research suite UI at `/kalpavriksha_ui/` |
| Runtime validation harness | `tests/test_runtime_validation.py` | Evidence capture with stub LLM |

---

## Deprecated / Archived (do not use)

| Path | Replaced by | Notes |
|------|-------------|-------|
| `archive/v0.9_legacy/` | v3 runtime | Old AGI loop, `chetna_core`, parallel memory |
| `archive/v3_legacy/frontend/app.js` | `frontend/index.html` | Legacy client; inline JS is canonical |
| `backend/api` route `/chetna` | `POST /api/chat` | Legacy response shape; kept for compat only |
| `src/chetnaos/orchestrator/*` (if present) | `cycle/`, `runtime/` | Removed in 7D2; any remnant is stale |
| Root `kalpavriksha/*.py` | `backend/plugins/kalpavriksha/` | Deleted in 7D2 |
| `organism/reasoning.py` shim | `reasoning/reasoning.py` | Deleted in 7D2 |
| `memory.db` fallback | `memory/*.json` + MemoryStore | No SQLite organism memory |
| `attached_assets/` paste files | — | Archived/deleted |

---

## Duplicate Functionality (resolved)

| Conflict | Winner | Loser |
|----------|--------|-------|
| Cognitive cycle | `cycle/cognitive_cycle.py` | `orchestrator/cognitive_cycle.py` |
| Runtime entry | `runtime/runtime.py` + `backend/runtime.py` | `orchestrator/runtime.py` |
| Reasoning | `reasoning/reasoning.py` | `organism/reasoning.py` |
| Agent tools | `tools/agent_tools.py` | `orchestrator/agent_tools.py` |
| State machine | `runtime/state_machine.py` | `orchestrator/state_machine.py` |
| Sleep manager | `runtime/sleep_manager.py` | `orchestrator/sleep_manager.py` |
| LLM router | `reasoning/llm_router.py` | `orchestrator/llm_router.py` |
| Kalpavriksha | `backend/plugins/kalpavriksha/` | root `kalpavriksha/` |
| Chat UI | `frontend/index.html` | `archive/v3_legacy/frontend/app.js` |

---

## Version Label Conflicts (cosmetic only)

| Location | Label | Canonical |
|----------|-------|-----------|
| `frontend/index.html` sidebar | "v2.0" | Should read **v3** (organism) |
| `backend/app.py` | v3.0.0 | **Active** |
| `cognitive_cycle.py` header | "v2.0" | Historical comment; code is v3 |
| `report.md` | "Runtime Science Phase" | Engineering report, not a second runtime |

**Rule:** One runtime (`ChetnaRuntime`), one cycle (`CognitiveCycle.run`), one memory tree (`memory/`).

---

## API Surface (production)

| Endpoint | Purpose |
|----------|---------|
| `POST /api/chat` | Chat + conversation persistence |
| `GET/POST/DELETE /api/conversations` | Conversation CRUD |
| `GET /api/workspace/session` | Refresh-safe workspace |
| `POST /api/agent` | Agent mode (same cycle) |
| `POST /api/goal` | Goal loop |
| `GET /api/dashboard` | Dashboard data |
| `GET /api/state` | Lightweight snapshot |
| `GET /health` | Health check |

---

## Migration Notes

1. Import from `src.chetnaos.cycle`, `runtime`, `reasoning`, `tools` — never `orchestrator`.
2. New persistence goes under `memory/` via `json_loader.memory_path`.
3. No new cognitive organs or pipeline stages without founder approval (`ARCHITECTURE_FREEZE.md`).
4. Kalpavriksha remains a plugin; not part of the core cycle.
