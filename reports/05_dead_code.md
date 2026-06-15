# 05 — Dead Code

**Analysis date:** 2026-06-15  
**Definition:** Code not reachable from any live entry point (`backend.app:app`)

---

## A. Fully Orphaned Packages

### `backend/agi/` — entire package (6 files, ~274 LOC)

| File | Reason Dead |
|------|-------------|
| `loop.py` | Not imported by `app.py` |
| `goal_agent.py` | `execute_goal()` has zero callers |
| `memory_service.py` | Only called from `loop.py` |
| `types.py` | Only used by agi package |
| `world_model.py` | Zero external imports |
| `__init__.py` | Exports unused symbols |

**Evidence:** `backend/app.py` `/api/goal` calls `rt.process(text, mode="goal")` — v2 runtime, not `backend.agi`.

---

### Legacy v1 kernel chain (~121 LOC)

```
backend/chetna_core.py
  ← backend/memory.py (Smriti)
  ← backend/dharma_net.py
  ← backend/world_state.py
  ← backend/evolution_engine.py
```

Only reachable via orphaned `backend/agi/loop.py`.

| Module | LOC | Notes |
|--------|-----|-------|
| `evolution_engine.py` | 14 | `adapt()` returns static string |
| `dharma_net.py` | 12 | Keyword filter, no LLM |
| `world_state.py` | 19 | Fake news array |
| `memory.py` (Smriti) | 29 | Separate SQLite schema |
| `chetna_core.py` | 47 | Pass-through pipeline |

---

## B. Empty Scaffold Files (13 files, 0 LOC)

Dead by definition — no implementation:

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
src/chetnaos/main.py
```

README advertises these as live capabilities. **They are not.**

---

## C. Instantiated But Never Called

| Module | Class | Instantiated In | Dead Method |
|--------|-------|---------------|-------------|
| `organism/embodiment.py` | `Embodiment` | `CognitiveCycle.__init__` | `act()` — ACT stage uses `Reasoning.reason()` |
| `reality/source_ranker.py` | `SourceRanker` | `RealityChecker.__init__` | `rank()`, `rank_output()` — never called in `check()` |
| `state_machine.py` | `CycleStage.DECIDE` | Enum defined | Never emitted in `run()` trace |

---

## D. Orphan Files (never imported)

| File | LOC | Notes |
|------|-----|-------|
| `organism/workspace.py` | 30 | Superseded by `workspace_state.py` |
| `tools/memory_audit.py` | 155 | CLI only — not part of runtime |
| `kalpavriksha/*.py` `__main__` blocks | — | Demo only |

---

## E. Broken Code Paths (reachable but non-functional)

| Location | Issue | Effect |
|----------|-------|--------|
| `organism/memory.py:30` | `_db.add()` does not exist | `store()` silently fails |
| `organism/memory.py:38` | `_db.recent()` does not exist | `recent()` always returns `[]` |
| `cognitive_cycle.py:294` | Calls broken `memory.store()` | Interactions never persisted to vector DB |
| `sleep.py:270` | Passes `self.memory` to consolidate | Recall works; store during cycle does not |

**Evidence from `memory/db.py`:** Only methods are `init_db()`, `upsert()`, `search()`.

---

## F. Unreachable Enum Values

```python
# state_machine.py
CycleStage.DECIDE = "DECIDE"  # defined but never used in cognitive_cycle.run()
```

Docstring claims 27 stages. Enum has 26 values. `run()` emits 25 distinct stage types per cycle (SLEEP/FORGET/CONSOLIDATE/WAKE always emitted).

---

## G. Dead Documentation

| File | Claim | Reality |
|------|-------|---------|
| `README.md` | Multi-agent coordination | Empty agent files |
| `README.md` | Autonomous workflows | Empty workflow files |
| `README.md` | `backend/agi/` core loop | Orphaned |
| `.agents/memory/chetnaos-arch.md` | 27-stage locked cycle | DECIDE unused; HABIT after PLAN not in doc order |

---

## H. Dead Code Volume Estimate

| Category | Files | LOC |
|----------|-------|-----|
| Orphaned backend/agi + v1 kernel | 11 | ~395 |
| Empty scaffolds | 13 | 0 |
| Orphan organism modules | 1 | 30 |
| Unused instantiated methods | 2 | ~51 |
| **Total removable** | **27** | **~476 (~10% of codebase)** |

---

## I. Recommended Deletions (Phase 1)

```
DELETE:
  backend/agi/
  backend/chetna_core.py
  backend/memory.py
  backend/dharma_net.py
  backend/world_state.py
  backend/evolution_engine.py
  backend/agents/          (all empty)
  backend/integrations/    (all empty)
  backend/workflows/       (all empty)
  src/chetnaos/organism/workspace.py

FIX (not delete):
  src/chetnaos/organism/memory.py  → use upsert()
  reality/source_ranker.py         → wire into check() or delete
  organism/embodiment.py           → wire act() or merge into action/
```
