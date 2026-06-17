# ChetnaOS — CLEAN TREE Audit

**Date:** 2026-06-17  
**Scope:** Read-only inventory. No files deleted.  
**Method:** `git ls-files`, directory glob, `rg` for imports/strings, AST import scan (scripts excluded as entry points), manual cross-check of CI gates.

---

## 1. Archive / legacy / backup directories

| Pattern | Found | Notes |
|---------|-------|-------|
| `archive/` | **Yes** | `archive/v0.9_legacy/` (13 files), `archive/v3_legacy/frontend/app.js` |
| `archive_v*` | **No** | No `archive_v*` top-level dirs |
| `legacy/` | **No** | Only inside `.venv` (third-party) |
| `old/` | **No** | Only inside `.venv` |
| `backup/` | **Partial** | `memory/.validation_backups/` (3 JSON rollback snapshots) |
| `deprecated/` | **No** | — |

### `archive/v0.9_legacy/` (13 files)

```
archive/v0.9_legacy/README.md
archive/v0.9_legacy/workspace.py
archive/v0.9_legacy/backend/chetna_core.py
archive/v0.9_legacy/backend/dharma_net.py
archive/v0.9_legacy/backend/evolution_engine.py
archive/v0.9_legacy/backend/memory.py
archive/v0.9_legacy/backend/world_state.py
archive/v0.9_legacy/backend/agi/__init__.py
archive/v0.9_legacy/backend/agi/goal_agent.py
archive/v0.9_legacy/backend/agi/loop.py
archive/v0.9_legacy/backend/agi/memory_service.py
archive/v0.9_legacy/backend/agi/types.py
archive/v0.9_legacy/backend/agi/world_model.py
```

### `archive/v3_legacy/` (1 file)

```
archive/v3_legacy/frontend/app.js
```

### `memory/.validation_backups/` (backup pattern)

```
memory/.validation_backups/beliefs_20260616T111603.json
memory/.validation_backups/beliefs_20260616T113333.json
memory/.validation_backups/beliefs_20260616T115129.json
```

### Local-only stale artifacts (not in git)

```
src/chetnaos/orchestrator/__pycache__/*.pyc   # 7 files from pre-7D2 shims
```

No tracked `src/chetnaos/orchestrator/*.py` on disk or in `git ls-files`.

---

## 2. Orchestrator references

### 2a. Python imports (`*.py`)

| File | Line | Kind | Text |
|------|------|------|------|
| — | — | **import** | **None** — no live `from src.chetnaos.orchestrator` or `import src.chetnaos.orchestrator` in production or test code |

### 2b. Strings / assertions (CI & gates)

| File | Line(s) | Kind | Text |
|------|---------|------|------|
| `scripts/phase7_gate.py` | 22 | label | `"No orchestrator shims (batch1)"` |
| `scripts/phase7_gate.py` | 24 | string | `find_spec('src.chetnaos.orchestrator.cognitive_cycle')` |
| `scripts/phase7_gate.py` | 27 | string | `Path('src/chetnaos/orchestrator')` |
| `scripts/phase7_gate.py` | 28–29 | strings | `cognitive_cycle.py`, `runtime.py`, `state_machine.py`, `sleep_manager.py`, `llm_router.py` must not exist |
| `scripts/phase7_gate.py` | 35 | string | `Path('src/chetnaos/orchestrator/agent_tools.py')` must not exist |

### 2c. Comments

| File | Line | Text |
|------|------|------|
| `src/chetnaos/cycle/cognitive_cycle.py` | 64 | `# Orchestrator` (section header only; not an import) |

### 2d. Tests

| File | orchestrator ref |
|------|------------------|
| `tests/*.py` | **None** |

### 2e. CI scripts

| File | Role |
|------|------|
| `.github/workflows/ci.yml` | Runs `python scripts/phase7_gate.py` (line 33); imports `src.chetnaos.runtime` not orchestrator (line 30) |
| `scripts/phase7_gate.py` | Batch1 negative assertions (see 2b) |

### 2f. Documentation / agent memory (historical; not executed)

| File | Notes |
|------|-------|
| `README.md` | Documents orchestrator removed in 7D2 |
| `PHASE7_RULES.md` | Rule 1: orchestrator core 5 shims |
| `docs/VERSION_MAP.md` | Migration map orchestrator → cycle/runtime/reasoning/tools |
| `archive/v0.9_legacy/README.md` | Historical paths |
| `.agents/memory/chetnaos-arch.md` | **Stale** — still cites `orchestrator/runtime` |
| `.agents/memory/MEMORY.md` | **Stale** — cites `orchestrator/runtime.py` |
| `reports/01_repository_inventory.md` | Historical inventory |
| `reports/02_dependency_graph.md` | **Stale** graph with orchestrator edges |
| `reports/04_duplicate_modules.md` | Historical duplicate analysis |
| `reports/07_target_architecture.md` | Target layout references |
| `reports/08_migration_plan.md` | Migration plan |
| `reports/09_final_folder_structure.md` | Target structure |
| `reports/10_build_order.md` | Build order |

---

## 3. Files with no import-path consumers

**Definition:** No other tracked `.py` file imports the module (AST `import` / `from`). Scripts and `tests/` treated as entry points and excluded from the “orphan” list. `__init__.py` package markers may still be loaded implicitly when a subpackage is imported.

### 3a. Confirmed orphans (zero-byte placeholders)

All **0 bytes**, git-tracked, **no importers**:

```
backend/agents/chat_agent.py
backend/agents/intent_detecter.py
backend/agents/scheduler_agent.py
backend/agents/voice_agent.py
backend/agents/whatsapp_agent.py
backend/integrations/emailer.py
backend/integrations/notifier.py
backend/integrations/telecrm_api.py
backend/integrations/whatsapp_web.py
backend/workflows/followup_flow.py
backend/workflows/lead_flow.py
backend/workflows/meeting_flow.py
```

### 3b. Standalone / unused by import graph

| File | Notes |
|------|-------|
| `tools/memory_audit.py` | CLI utility; no imports from rest of codebase |
| `src/chetnaos/main.py` | Empty file |
| `src/chetnaos/memory/compat.py` | Documented compat re-export; **no current importers** |
| `src/chetnaos/dashboard/snapshot.py` | Thin delegate; API uses `cycle.dashboard_snapshot()` directly |
| `src/chetnaos/dashboard/runtime_inspector.py` | Thin delegate; runtime/cycle call `_runtime_inspection_snapshot()` inline |
| `src/chetnaos/dashboard/__init__.py` | Re-exports above; **no importers** |
| `src/chetnaos/learning/__init__.py` | Re-export shim to `cognition/`; **no importers** (cycle imports `cognition` directly) |
| `src/chetnaos/learning/belief_revision.py` | Re-export shim |
| `src/chetnaos/learning/skill_engine.py` | Re-export shim to `organism.skills` |
| `backend/agent.py` | Shim → `backend.api.agent`; **no importers** (CI imports `backend.api.agent` directly) |
| `archive/**` | Entire tree — **no Python imports** from live code |

### 3c. Compat shims — imported only by gates/tests (not production path)

`src/chetnaos/organs/*/__init__.py` (24 organ packages): imported by `scripts/phase_v3_2_gate.py`, `tests/test_decide_trace.py`, `scripts/gen_organ_shims.py`. Production cycle uses `src.chetnaos.organism.*` directly.

`src/chetnaos/memory_kernel/episodic_memory.py` (and semantic/procedural/working_memory): one-line re-exports to `src.chetnaos.memory.*`; live path uses `memory_kernel.memory_item` + `memory.store`.

---

## 4. Duplicate implementations

### 4a. Runtime

| Role | Canonical (live) | Duplicate / legacy |
|------|------------------|-------------------|
| HTTP singleton | `backend/runtime.py` → lazy `ChetnaRuntime` | — |
| Core runtime | `src/chetnaos/runtime/runtime.py` | `archive/v0.9_legacy/backend/chetna_core.py` (historical) |
| State machine | `src/chetnaos/runtime/state_machine.py` | Stale `orchestrator/__pycache__/state_machine*.pyc` |
| Sleep manager | `src/chetnaos/runtime/sleep_manager.py` | Stale `orchestrator/__pycache__/sleep_manager*.pyc` |
| Executive | `src/chetnaos/runtime/executive_controller.py` | — |
| Dashboard inspect | Inline `CognitiveCycle._runtime_inspection_snapshot()` | `src/chetnaos/dashboard/runtime_inspector.py` (unused delegate) |

### 4b. Cognitive cycle

| Role | Canonical | Duplicate / legacy |
|------|-----------|-------------------|
| 26-stage cycle | `src/chetnaos/cycle/cognitive_cycle.py` | `archive/v0.9_legacy/backend/agi/loop.py` |
| — | — | Stale `orchestrator/__pycache__/cognitive_cycle*.pyc` |

### 4c. Reasoning

| Role | Canonical | Duplicate / legacy |
|------|-----------|-------------------|
| LLM reasoning | `src/chetnaos/reasoning/reasoning.py` | — |
| Prompt assembly | `src/chetnaos/reasoning/prompt_builder.py` | — |
| Context | `src/chetnaos/reasoning/context_builder.py`, `conversation_context.py` | — |
| LLM router | `src/chetnaos/reasoning/llm_router.py` | Stale `orchestrator/__pycache__/llm_router*.pyc` |
| Honesty guard | `src/chetnaos/reasoning/honesty_guard.py` | — |
| Reflection eval | `reflection/reflection_v2.py` | Used by `organism/reflection.py` (top-level `reflection/` pkg, not under `src/`) |

### 4d. Memory

| Role | Canonical | Duplicate / legacy |
|------|-----------|-------------------|
| SQLite vector store | `memory/db.py` | `archive/v0.9_legacy/backend/memory.py`, `agi/memory_service.py` |
| Unified facade | `src/chetnaos/memory/store.py` | `src/chetnaos/memory_kernel/memory_store.py` (re-export) |
| Episodic / semantic / procedural / WM | `src/chetnaos/memory/{episodic,semantic,procedural,working_memory}.py` | `memory_kernel/*_memory.py` (re-exports) |
| JSON loaders / validation | `src/chetnaos/memory/json_loader.py`, `validation.py`, `health.py` | — |
| Compat layer | — | `src/chetnaos/memory/compat.py` (unused) |
| Organism memory API | `src/chetnaos/organism/memory.py` | — |

### 4e. Agent tools

| Role | Canonical | Duplicate / legacy |
|------|-----------|-------------------|
| Tool execution | `src/chetnaos/tools/agent_tools.py` | Stale `orchestrator/__pycache__/agent_tools*.pyc` |
| Facades | `tools/calculator.py`, `web_search.py`, `document_reader.py`, `tool_router.py` | All re-export/wrap `agent_tools` |

### 4f. Cross-cutting shim layers (not full duplicates, but parallel paths)

| Layer | Points to |
|-------|-----------|
| `src/chetnaos/learning/*` | `src/chetnaos/cognition/*`, `organism/skills` |
| `src/chetnaos/organs/*` | `src/chetnaos/organism/*`, `cognition/*` |
| `src/chetnaos/memory_kernel/*` | `src/chetnaos/memory/*` |
| `backend/agent.py` | `backend/api/agent.py` |

---

## 5. FILE | REFERENCED_BY | SAFE_TO_DELETE

**Legend for SAFE_TO_DELETE**

| Value | Meaning |
|-------|---------|
| **YES** | No import consumers; safe to remove from a clean-tree perspective |
| **NO** | Actively imported or required by CI/runtime |
| **CAUTION** | Intentional archive, rollback data, compat shim, or standalone tool — review before delete |
| **YES (local)** | Not git-tracked; safe to delete from working tree |

### Archive & stale artifacts

| FILE | REFERENCED_BY | SAFE_TO_DELETE |
|------|---------------|----------------|
| `archive/v0.9_legacy/**` | Docs only (`README`, `VERSION_MAP`) | **CAUTION** — keep as historical reference unless policy says remove |
| `archive/v3_legacy/frontend/app.js` | None | **CAUTION** — same as above |
| `memory/.validation_backups/*.json` | `src/chetnaos/memory/validation.py` (rollback) | **NO** |
| `src/chetnaos/orchestrator/__pycache__/*.pyc` | None (stale bytecode) | **YES (local)** |

### Empty backend placeholders

| FILE | REFERENCED_BY | SAFE_TO_DELETE |
|------|---------------|----------------|
| `backend/agents/chat_agent.py` | None | **YES** |
| `backend/agents/intent_detecter.py` | None | **YES** |
| `backend/agents/scheduler_agent.py` | None | **YES** |
| `backend/agents/voice_agent.py` | None | **YES** |
| `backend/agents/whatsapp_agent.py` | None | **YES** |
| `backend/integrations/emailer.py` | None | **YES** |
| `backend/integrations/notifier.py` | None | **YES** |
| `backend/integrations/telecrm_api.py` | None | **YES** |
| `backend/integrations/whatsapp_web.py` | None | **YES** |
| `backend/workflows/followup_flow.py` | None | **YES** |
| `backend/workflows/lead_flow.py` | None | **YES** |
| `backend/workflows/meeting_flow.py` | None | **YES** |

### Unused shims & dead delegates

| FILE | REFERENCED_BY | SAFE_TO_DELETE |
|------|---------------|----------------|
| `backend/agent.py` | None (`backend.api.agent` used directly) | **CAUTION** — remove only after confirming no external `backend.agent` imports |
| `src/chetnaos/main.py` | None (empty) | **YES** |
| `src/chetnaos/memory/compat.py` | None | **CAUTION** — documented compat; delete after import audit |
| `src/chetnaos/dashboard/__init__.py` | None | **CAUTION** — part of v3 dashboard package |
| `src/chetnaos/dashboard/snapshot.py` | `dashboard/__init__.py` only | **CAUTION** |
| `src/chetnaos/dashboard/runtime_inspector.py` | `dashboard/__init__.py` only | **CAUTION** |
| `src/chetnaos/learning/__init__.py` | None | **CAUTION** — v3 layer shim |
| `src/chetnaos/learning/belief_revision.py` | `learning/__init__.py` | **CAUTION** |
| `src/chetnaos/learning/skill_engine.py` | `learning/__init__.py` | **CAUTION** |
| `tools/memory_audit.py` | None (CLI entry) | **CAUTION** — useful manual audit script |

### Compat re-export duplicates (keep until migration completes)

| FILE | REFERENCED_BY | SAFE_TO_DELETE |
|------|---------------|----------------|
| `src/chetnaos/memory_kernel/episodic_memory.py` | None direct; canonical used | **NO** — gate `phase_v3_1_gate` imports `memory_kernel` |
| `src/chetnaos/memory_kernel/semantic_memory.py` | None direct | **NO** |
| `src/chetnaos/memory_kernel/procedural_memory.py` | None direct | **NO** |
| `src/chetnaos/memory_kernel/working_memory.py` | None direct | **NO** |
| `src/chetnaos/memory_kernel/memory_store.py` | `phase_v3_1_gate` | **NO** |
| `src/chetnaos/memory_kernel/memory_item.py` | `memory/store.py`, `reasoning/prompt_builder.py`, tests | **NO** |
| `src/chetnaos/organs/*/__init__.py` (×24) | `phase_v3_2_gate`, `test_decide_trace.py` | **NO** |

### Canonical live modules (must keep)

| FILE | REFERENCED_BY | SAFE_TO_DELETE |
|------|---------------|----------------|
| `src/chetnaos/runtime/runtime.py` | `backend/runtime.py`, `phase7_gate`, CI | **NO** |
| `backend/runtime.py` | `backend/app.py`, API routes | **NO** |
| `src/chetnaos/cycle/cognitive_cycle.py` | `runtime/runtime.py`, tests, gates | **NO** |
| `src/chetnaos/reasoning/reasoning.py` | `cognitive_cycle.py`, tests, `phase7_gate` | **NO** |
| `src/chetnaos/tools/agent_tools.py` | `cognitive_cycle.py`, `tool_router.py` | **NO** |
| `memory/db.py` | `memory/store.py`, `backend/app.py`, tests | **NO** |
| `src/chetnaos/memory/store.py` | `organism/memory.py`, API, scripts, tests | **NO** |
| `reflection/reflection_v2.py` | `organism/reflection.py`, `phase1_gate` | **NO** |
| `scripts/phase7_gate.py` | `.github/workflows/ci.yml` | **NO** |

### Stale documentation (orchestrator)

| FILE | REFERENCED_BY | SAFE_TO_DELETE |
|------|---------------|----------------|
| `.agents/memory/chetnaos-arch.md` | Agent memory | **CAUTION** — update, don't delete |
| `.agents/memory/MEMORY.md` | Agent memory | **CAUTION** — update, don't delete |
| `reports/02_dependency_graph.md` | Human reports | **CAUTION** — supersede with this audit |

---

## 6. Recommended clean-tree actions (report only — not executed)

1. **Delete local stale bytecode:** `src/chetnaos/orchestrator/__pycache__/` (7 `.pyc` files).
2. **Remove or implement empty placeholders:** `backend/agents/`, `integrations/`, `workflows/` (12 zero-byte files).
3. **Update stale docs:** `.agents/memory/*`, `reports/02_dependency_graph.md` — point to `cycle/`, `runtime/`, `reasoning/`, `tools/`.
4. **Defer shim consolidation** until explicit migration: `memory_kernel/`, `organs/`, `learning/`, `dashboard/` delegates.
5. **Keep `archive/`** unless product policy allows historical removal.

---

## 7. CI clean-tree status

| Check | Expected on clean checkout |
|-------|---------------------------|
| `git ls-files src/chetnaos/orchestrator/*.py` | Empty |
| `phase7_gate` batch1 | Pass (asserts shims absent) |
| Local disk | `orchestrator/__pycache__/` only — **does not fail batch1** (checks `.py` files, not `.pyc`) |

**Note:** If CI reports `FAIL: No orchestrator shims (batch1)`, a tracked `.py` shim was reintroduced under `src/chetnaos/orchestrator/`. Stale `.pyc` alone does not trigger batch1.
