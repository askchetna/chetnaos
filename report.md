# ChetnaOS — Runtime Science Phase

**Last updated:** 2026-06-16 (Guruji approval)  
**Architecture:** LOCKED — see `ARCHITECTURE_FREEZE.md`

```powershell
python scripts/phase7_gate.py          # 8/8 PASS
python scripts/phase8_experiment1_gate.py  # 10-cycle smoke
python scripts/experiment_1_soak.py    # full 100-cycle run
```

---

## Guruji's Verdict — Accepted

| Transition | Status |
|------------|--------|
| Architecture design → Runtime science | **ENTERED** |
| 7D2 shim removal | **COMPLETE** (2 batches, all gates green) |
| Phase 8 Experiment 1 | **READY** (script + 10-cycle smoke PASS) |
| Architecture freeze | **LOCKED** |

---

## 7D2 Complete (migration, not cleanup)

### Batch 1 — removed
- `orchestrator/cognitive_cycle.py`
- `orchestrator/runtime.py`
- `orchestrator/state_machine.py`
- `orchestrator/sleep_manager.py`
- `orchestrator/llm_router.py`

### Batch 2 — removed
- `orchestrator/agent_tools.py`
- `organism/reasoning.py`
- Root `kalpavriksha/*.py` (canonical: `backend/plugins/kalpavriksha/`)

### Canonical paths (use these)
```
src/chetnaos/cycle/cognitive_cycle.py
src/chetnaos/runtime/runtime.py
src/chetnaos/runtime/state_machine.py
src/chetnaos/reasoning/reasoning.py
src/chetnaos/tools/agent_tools.py
backend/plugins/kalpavriksha/
```

**No logic changes.** Import fixes only. All gates green.

---

## Phase 8 Experiment 1 — 100-cycle soak

**Observe only.** No architecture changes.

```powershell
python scripts/experiment_1_soak.py              # 100 cycles
python scripts/experiment_1_soak.py --cycles 10  # quick smoke
```

**Output:** `reports/experiment_1_soak.json`

### Per-cycle metrics logged
`cycle_id`, `identity_hash`, `belief_hash`, `goal_hash`, `memory_count`, `working_memory_count`, `contradictions`, `sleep_triggered`, `forget_count`, `reflection_quality`, `decision_confidence`, `execution_time_ms`

### 10-cycle smoke results (evidence)
| Metric | Cycle 1 | Cycle 10 | Changed |
|--------|---------|----------|---------|
| identity_hash | 66f5458c… | 8ae3b467… | **Yes** |
| belief_hash | 32f2cfc… | bd4615b… | **Yes** |
| goal_hash | c3e66c51… | c3e66c51… | No |
| working_memory_count | 1 | 7 | **Yes** |
| contradictions | 0 | 0 | No |

---

## Scientific Validation Score (honest)

| Property | Score |
|----------|-------|
| Cognitive Architecture | 9.2/10 |
| Runtime Design | 8.8/10 |
| Memory System | 8.7/10 |
| Engineering Discipline | 8.5/10 |
| Future Research Potential | 9.3/10 |
| **Scientific Validation** | **4.5/10 → improving with experiments** |
| Proven AGI | Unknown |

---

## Research thesis (paper-ready statement)

> ChetnaOS is a developmental cognitive architecture designed to study whether repeated interaction with the environment can gradually reshape memory, beliefs, identity, goals, and future behavior across multiple timescales.

---

## What's next (Guruji's 30-day plan)

| Week | Focus | Status |
|------|-------|--------|
| 1 | 7D2 | ✅ Done |
| 2 | 100-cycle soak | **Run now** (`experiment_1_soak.py`) |
| 3 | Founder disappears simulation | Pending approval |
| 4 | Contradictory evidence experiment | Pending approval |

**No new architecture. No new organs. Only experiments.**

---

## Remaining cleanup (optional, low priority)

- Remove empty `src/chetnaos/orchestrator/` directory
- Move `organism/*.py` → `organs/*/` (Phase 9+, not now)
- `pyproject.toml` package install
