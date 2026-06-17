# Clean-Tree Deletion Report

**Date:** 2026-06-17  
**Source audit:** `reports/clean_tree_audit.md`  
**Rule:** Delete only rows marked **YES** or **YES (local)**. Skipped all **CAUTION** and **NO** rows.

---

## 1. Files deleted

### Git-tracked (13 files)

| File | Size | Reason |
|------|------|--------|
| `backend/agents/chat_agent.py` | 0 B | Empty placeholder; no importers |
| `backend/agents/intent_detecter.py` | 0 B | Empty placeholder; no importers |
| `backend/agents/scheduler_agent.py` | 0 B | Empty placeholder; no importers |
| `backend/agents/voice_agent.py` | 0 B | Empty placeholder; no importers |
| `backend/agents/whatsapp_agent.py` | 0 B | Empty placeholder; no importers |
| `backend/integrations/emailer.py` | 0 B | Empty placeholder; no importers |
| `backend/integrations/notifier.py` | 0 B | Empty placeholder; no importers |
| `backend/integrations/telecrm_api.py` | 0 B | Empty placeholder; no importers |
| `backend/integrations/whatsapp_web.py` | 0 B | Empty placeholder; no importers |
| `backend/workflows/followup_flow.py` | 0 B | Empty placeholder; no importers |
| `backend/workflows/lead_flow.py` | 0 B | Empty placeholder; no importers |
| `backend/workflows/meeting_flow.py` | 0 B | Empty placeholder; no importers |
| `src/chetnaos/main.py` | 0 B | Empty file; no importers |

### Local-only (not git-tracked)

| Path | Count | Reason |
|------|-------|--------|
| `src/chetnaos/orchestrator/__pycache__/*.pyc` | 7 | Stale pre-7D2 bytecode |
| `src/chetnaos/orchestrator/` (empty dir) | 1 | Removed after `__pycache__` cleared |

**Total removed:** 13 tracked deletions + 7 `.pyc` files + 1 empty directory.

---

## 2. Files intentionally NOT deleted

Per audit **CAUTION** / **NO** (examples):

- `archive/**` — historical reference
- `memory/.validation_backups/*.json` — rollback data
- `backend/agent.py`, `src/chetnaos/memory/compat.py` — compat shims
- `src/chetnaos/dashboard/*`, `src/chetnaos/learning/*` — v3 shim layers
- `tools/memory_audit.py` — standalone CLI
- All runtime, cycle, reasoning, memory, CI gate modules

---

## 3. Post-deletion verification

| Check | Result |
|-------|--------|
| `from backend.app import app` | **PASS** |
| `phase7_gate` — DECIDE, cycle, runtime, memory, reasoning, batch2, runtime validation | **PASS** (7/8 checks) |
| `phase7_gate` — batch1 orchestrator shims | **FAIL** (see §4) |

No deleted file was referenced by imports, tests, or CI entrypoints.

---

## 4. Side effect: phase7 batch1 after `orchestrator/` removal

Before deletion, `src/chetnaos/orchestrator/__pycache__/` existed (stale `.pyc` only).  
After removing `__pycache__` and the empty `orchestrator/` directory:

```text
importlib.util.find_spec('src.chetnaos.orchestrator.cognitive_cycle')
→ ModuleNotFoundError: No module named 'src.chetnaos.orchestrator'
```

`scripts/phase7_gate.py` batch1 does not catch this exception; it expects `find_spec` to return `None`. On a truly clean tree with no `orchestrator/` package at all, batch1 fails the same way.

**This is not caused by deleting the 13 placeholder files.** Fix (separate task): wrap batch1 `find_spec` in try/except `ModuleNotFoundError`, or treat missing parent package as pass.

---

## 5. `git grep` results (tracked files only)

### `git grep orchestrator`

| File | Context |
|------|---------|
| `.agents/memory/MEMORY.md` | Stale entry point reference |
| `.agents/memory/chetnaos-arch.md` | Stale import examples (×3) |
| `PHASE7_RULES.md` | Rule 1: orchestrator shims |
| `README.md` | 7D2 removal note |
| `archive/v0.9_legacy/README.md` | Historical mapping (×2) |
| `docs/VERSION_MAP.md` | Migration map (×8) |
| `reports/01_repository_inventory.md` | Historical inventory (×3) |
| `reports/02_dependency_graph.md` | Stale dependency graph (×6) |
| `reports/04_duplicate_modules.md` | Historical duplicates (×3) |
| `reports/07_target_architecture.md` | Target layout comment |
| `reports/08_migration_plan.md` | Migration step |
| `reports/09_final_folder_structure.md` | Target structure (×6) |
| `reports/10_build_order.md` | Build order note |
| `scripts/phase7_gate.py` | **CI** — negative assertions (×4) |

**Live Python imports of `orchestrator`:** none (only `phase7_gate.py` strings).

### `git grep legacy`

| File | Context |
|------|---------|
| `backend/api/chat.py` | `chetna_legacy` endpoint name (live API) |
| `docs/VERSION_MAP.md` | `archive/v0.9_legacy`, `v3_legacy` paths (×3) |
| `reports/01_repository_inventory.md` | Repo description |
| `reports/04_duplicate_modules.md` | README legacy name |
| `reports/12_memory_migration_readiness.md` | Archived Smriti reference |
| `src/chetnaos/memory/compat.py` | Docstring: legacy memory entry points |
| `src/chetnaos/reasoning/reasoning.py` | Docstring: legacy callers |

### `git grep archive`

| File | Context |
|------|---------|
| `archive/v0.9_legacy/README.md` | Do-not-import notice |
| `docs/VERSION_MAP.md` | Archive path mapping (×3) |
| `reports/12_memory_migration_readiness.md` | Archived Smriti (×2) |
| `scripts/phase1_gate.py` | Verify kernel without archived v0.9 stack |

**`archive/` tree:** unchanged (14 files retained).

---

## 6. Git status (deletions only)

```text
 D backend/agents/chat_agent.py
 D backend/agents/intent_detecter.py
 D backend/agents/scheduler_agent.py
 D backend/agents/voice_agent.py
 D backend/agents/whatsapp_agent.py
 D backend/integrations/emailer.py
 D backend/integrations/notifier.py
 D backend/integrations/telecrm_api.py
 D backend/integrations/whatsapp_web.py
 D backend/workflows/followup_flow.py
 D backend/workflows/lead_flow.py
 D backend/workflows/meeting_flow.py
 D src/chetnaos/main.py
```

---

## 7. Recommended follow-ups

1. **Fix `phase7_gate` batch1** — handle missing `src.chetnaos.orchestrator` package (ModuleNotFoundError).
2. **Update stale docs** — `.agents/memory/*`, `reports/02_dependency_graph.md` still cite live orchestrator paths.
3. **Optional:** remove empty `backend/agents/`, `integrations/`, `workflows/` directories if git allows (dirs may remain after file deletion).
4. **Stage & commit** deletions when ready (`git add -u` on deleted paths only).
