# 04 — Duplicate Modules

**Analysis date:** 2026-06-15

---

## A. Critical Duplicates (same concept, different implementations)

### 1. World Model / World State (3 implementations)

| # | Path | Class | Data Model | Wired To |
|---|------|-------|------------|----------|
| 1 | `backend/world_state.py` | `WorldState` | time, day, energy, news | `chetna_core` (orphaned) |
| 2 | `backend/agi/world_model.py` | `WorldModel` | Thin adapter over #1 | Nothing (orphaned) |
| 3 | `src/chetnaos/organism/world_model.py` | `WorldModel` | topics, entities, interaction_count | `cognitive_cycle` (**LIVE**) |

**Conflict:** Same class name `WorldModel` in two packages. Different semantics.

**Recommendation:** Keep #3 only. Delete #1 and #2 after migration.

---

### 2. Memory (3 modules, 1 database file)

| # | Path | Class | Storage | API |
|---|------|-------|---------|-----|
| 1 | `backend/memory.py` | `Smriti` | `mem.db` → table `smriti` | `store_event(type, content, ts)` |
| 2 | `memory/db.py` | `MemoryDB` | `mem.db` → table `memories` | `upsert()`, `search()` |
| 3 | `src/chetnaos/organism/memory.py` | `Memory` | Wraps #2 | `recall()`, `store()` (broken), `recent()` (broken) |

**Conflict:** Two schemas in one SQLite file. `Memory.store()` calls non-existent `add()` instead of `upsert()`.

**Recommendation:** Single `memory/` package with one `MemoryStore` class.

---

### 3. Dharma / Values / Reflection (3 layers)

| # | Path | Role |
|---|------|------|
| 1 | `backend/dharma_net.py` | `DharmaFilter` — keyword filter on input (orphaned) |
| 2 | `src/chetnaos/constitution/*` | Static mission/values/ethics dicts |
| 3 | `reflection/reflection_v2.py` | Post-hoc decision scoring via `dharma_rules.json` |

**Conflict:** Three separate value-enforcement mechanisms with no unified interface.

**Recommendation:** Merge into `values/dharma_engine.py`.

---

### 4. Workspace (2 modules)

| # | Path | Class | Status |
|---|------|-------|--------|
| 1 | `src/chetnaos/organism/workspace.py` | `Workspace` | In-memory, **orphaned** |
| 2 | `src/chetnaos/organism/workspace_state.py` | `WorkspaceState` | JSON persistence, **LIVE** |

**Recommendation:** Delete `workspace.py`. Rename `workspace_state.py` → `workspace/manager.py`.

---

### 5. Contradiction Handling (2 modules)

| # | Path | Class | Scope |
|---|------|-------|-------|
| 1 | `src/chetnaos/organism/contradiction_tracker.py` | `ContradictionTracker` | Cross-belief/memory/founder scan |
| 2 | `src/chetnaos/organism/reality/contradiction_detector.py` | `ContradictionDetector` | Per-output check |

**Not a true duplicate** — different scopes. But overlapping responsibility.

**Recommendation:** `ContradictionDetector` feeds `ContradictionTracker`; single public API.

---

### 6. Sleep Management (2 modules)

| # | Path | Class | Role |
|---|------|-------|------|
| 1 | `src/chetnaos/orchestrator/sleep_manager.py` | `SleepManager` | When to sleep (every N cycles) |
| 2 | `src/chetnaos/organism/sleep.py` | `Sleep` | What happens during sleep |

**Not duplicate** — complementary. Keep both under `memory/consolidation/`.

---

### 7. AGI Loop vs Cognitive Cycle (2 orchestrators)

| # | Path | Entry | Stages |
|---|------|-------|--------|
| 1 | `backend/agi/loop.py` | `run_loop(goal)` | Recursive ChetnaCore + reflection |
| 2 | `src/chetnaos/orchestrator/cognitive_cycle.py` | `run(input, mode)` | 26-stage developmental cycle |

**Conflict:** README and `backend/agi/` describe v0.9 loop. Live app uses v2 cycle exclusively.

**Recommendation:** Delete v0.9 loop or explicitly subsume as `planning/goal_loop.py` mode.

---

### 8. Reflection (2 modules)

| # | Path | Role |
|---|------|------|
| 1 | `reflection/reflection_v2.py` | Rule-based dharma scoring |
| 2 | `src/chetnaos/organism/reflection.py` | Thin wrapper calling #1 |

**Acceptable** — wrapper pattern. Move both under `values/` or `meta_cognition/`.

---

## B. Naming Inconsistencies

| Issue | Evidence |
|-------|----------|
| `intent_detecter` typo | `backend/agents/intent_detecter.py` (should be `detector`) |
| `play_mod` vs `Play` | `cognitive_cycle.py` uses `self.play_mod` to avoid keyword clash |
| `CycleStage.DECIDE` unused | Enum has DECIDE; cycle uses EVALUATE instead |
| `src.chetnaos` vs `backend` import style | Mix of `from src.chetnaos...` and `from backend...` |
| `sys.path.insert` hack | `organism/memory.py` manipulates `sys.path` |
| README says "ChetnaGPT" | `README.md` line 123 — legacy name |
| `backend\app.py` vs `backend/app.py` | Duplicate path entries on Windows (same file) |

---

## C. Duplicate Data Stores

| File | Written By | Overlap |
|------|-----------|---------|
| `memory/beliefs.json` | `beliefs.py`, `sleep.py` (prune) | — |
| `memory/experiences.jsonl` | `experience.py`, read by `sleep.py` | — |
| `memory/contradictions.json` | `contradiction_tracker.py` | — |
| `mem.db` | Smriti + MemoryDB | **Schema collision risk** |

---

## D. Merge Matrix

| Merge Into | Absorb |
|------------|--------|
| `memory/store.py` | `memory/db.py`, `organism/memory.py`, `backend/memory.py` |
| `world_model/engine.py` | `organism/world_model.py` only |
| `values/dharma_engine.py` | `dharma_net.py`, `reflection_v2.py`, constitution ethics scoring |
| `workspace/manager.py` | `workspace_state.py`, delete `workspace.py` |
| `cognition/executive.py` | Extract from `cognitive_cycle.py` |
| `planning/goal_manager.py` | `purpose.py` + `self_trainer.py` goal logic |
