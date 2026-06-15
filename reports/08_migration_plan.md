# 08 — Migration Plan

**Analysis date:** 2026-06-15  
**Strategy:** Incremental migration with continuous deployability. Each phase leaves the app running.

---

## Phase 1 — Stabilize & Delete Dead Weight (Week 1)

**Goal:** Fix critical bugs. Remove orphaned code. No architectural moves yet.

### Tasks

| # | Task | Risk |
|---|------|------|
| 1.1 | Fix `organism/memory.py`: `store()` → `memory_db.upsert()`, add `recent()` to `MemoryDB` | Low |
| 1.2 | Remove silent `except: pass` on persistence — log errors | Low |
| 1.3 | Delete `backend/agi/` (6 files) | None — orphaned |
| 1.4 | Delete `backend/chetna_core.py`, `memory.py`, `dharma_net.py`, `world_state.py`, `evolution_engine.py` | None — orphaned |
| 1.5 | Delete 13 empty scaffold files + empty directories | None |
| 1.6 | Delete `organism/workspace.py` (orphaned) | None |
| 1.7 | Wire `source_ranker` into `RealityChecker.check()` OR delete | Low |
| 1.8 | Wire `embodiment.act()` into ACT stage OR delete | Low |
| 1.9 | Update `README.md` to reflect v2 architecture honestly | None |
| 1.10 | Add `tests/test_memory_store.py` — verify upsert + search | Low |

### Exit Criteria

- [ ] `memory.store()` persists to `mem.db` (verified by test)
- [ ] `smoke.ps1` passes
- [ ] No orphaned Python imports
- [ ] README matches reality

### Files Removed (~476 LOC)

```
backend/agi/*
backend/chetna_core.py, memory.py, dharma_net.py, world_state.py, evolution_engine.py
backend/agents/*, backend/integrations/*, backend/workflows/*
src/chetnaos/organism/workspace.py
src/chetnaos/main.py (empty)
```

---

## Phase 2 — Unify Memory & Values (Week 2–3)

**Goal:** Single memory subsystem. Single dharma layer.

### Tasks

| # | Task |
|---|------|
| 2.1 | Create `chetnaos/memory/store.py` — merge `memory/db.py` + `organism/memory.py` |
| 2.2 | Add `MemoryStore.recent(n)` — temporal query on `created_at` |
| 2.3 | Migrate Smriti `smriti` table data into `memories` (if any exists) |
| 2.4 | Create `chetnaos/memory/episodic.py` from `experience.py` |
| 2.5 | Create `chetnaos/memory/semantic.py` from `beliefs.py` + `learning.py` |
| 2.6 | Create `chetnaos/memory/procedural.py` from `skills.py` + `habit.py` |
| 2.7 | Create `chetnaos/values/dharma_engine.py` — merge `reflection_v2.py` logic |
| 2.8 | Create `chetnaos/values/constitution.py` — merge constitution modules |
| 2.9 | Update `reasoning.py` and `reflection.py` imports |
| 2.10 | Add schema validation for JSON memory files (pydantic models) |

### Exit Criteria

- [ ] One `MemoryStore` class, one SQLite schema
- [ ] One `DharmaEngine` class
- [ ] Episodic recall available in RECALL stage
- [ ] All existing JSON data preserved

---

## Phase 3 — Restructure Packages (Week 4–6)

**Goal:** Move from flat `organism/` to target domain packages.

### Tasks

| # | Task |
|---|------|
| 3.1 | Add `pyproject.toml` with package `chetnaos` |
| 3.2 | Create target directory structure (see `09_final_folder_structure.md`) |
| 3.3 | Move modules with `git mv` preserving history |
| 3.4 | Extract `ExecutiveController` from `cognitive_cycle.py` |
| 3.5 | Slim `cognitive_cycle.py` to stage dispatch only (~150 LOC) |
| 3.6 | Move `backend/app.py` → `chetnaos/infrastructure/app.py` |
| 3.7 | Move `backend/config.py` → `chetnaos/infrastructure/config.py` |
| 3.8 | Move `orchestrator/*` → `chetnaos/infrastructure/` |
| 3.9 | Move `backend/agent.py` tools → `chetnaos/tools/` + `chetnaos/agents/` |
| 3.10 | Create `chetnaos/action/executor.py` — bridge decision → tools |
| 3.11 | Create new modules: `self_model`, `curiosity`, `emotion`, `goal_manager`, `belief_revision`, `social_learning`, `working_memory` |
| 3.12 | Update `Procfile` and `smoke.ps1` entry points |
| 3.13 | Compatibility shim: `src/chetnaos/` re-exports from `chetnaos/` (deprecation warnings) |

### Exit Criteria

- [ ] `from chetnaos.infrastructure.runtime import ChetnaRuntime` works
- [ ] `cognitive_cycle.py` < 200 LOC
- [ ] `uvicorn chetnaos.infrastructure.app:app` serves all endpoints
- [ ] Deprecation shims warn but don't break

---

## Phase 4 — Cognitive Completeness & Production (Week 7–10)

**Goal:** Close AGI gaps. Production hardening.

### Tasks

| # | Task |
|---|------|
| 4.1 | Implement `GoalManager` — multi-goal stack with `/api/goal` integration |
| 4.2 | Implement `CuriosityDrive` — feeds exploration goals from workspace questions |
| 4.3 | Implement `SelfModel` — capability map from skills + development |
| 4.4 | Implement `BeliefRevisionEngine` — evidence-weighted updates |
| 4.5 | Implement `WorkingMemory` — bounded buffer with eviction |
| 4.6 | Wire meta-cognition feedback into next cycle's attention |
| 4.7 | Persist `world_model` to disk (not in-memory only) |
| 4.8 | Fix CORS: specific origins, not `*` + credentials |
| 4.9 | Replace `eval()` in calculator with `ast` literal eval |
| 4.10 | Add SSRF protection to web_fetch (host allowlist) |
| 4.11 | Replace `@app.on_event("startup")` with lifespan handler |
| 4.12 | Comprehensive test suite: cycle integration test, memory test, dharma test |
| 4.13 | CI: run tests on every PR |
| 4.14 | Remove `src/chetnaos/` compatibility shim |
| 4.15 | AGI readiness re-assessment (target: 60+/100) |

### Exit Criteria

- [ ] All cognitive components at PARTIAL or better (see `03_missing_modules.md`)
- [ ] Test coverage > 60% on `chetnaos/` package
- [ ] Security issues from gap analysis resolved
- [ ] Single architecture documented and deployed

---

## Risk Matrix

| Risk | Phase | Mitigation |
|------|-------|------------|
| Breaking `/api/chat` during restructure | 3 | Compatibility shims + smoke tests |
| Data loss during memory merge | 2 | Backup `memory/` before migration |
| Import path churn | 3 | Deprecation period with re-exports |
| Scope creep on new modules | 4 | Minimal viable implementations first |

---

## Rollback Strategy

Each phase is a separate branch. If Phase N fails:

1. Revert branch
2. Previous phase remains deployable
3. Phase 1 fixes (memory store) should be merged to main immediately regardless

---

## Success Metrics

| Metric | Current | Phase 1 | Phase 4 Target |
|--------|---------|---------|----------------|
| AGI readiness score | 38/100 | 42 | 60+ |
| Orphaned LOC | ~476 | 0 | 0 |
| Memory store success rate | 0% (broken) | 100% | 100% |
| Test files | 0 | 1 | 20+ |
| Package count (flat organism) | 1 | 1 | 14 domains |
| Cognitive components MISSING | 8 | 6 | 0 |
