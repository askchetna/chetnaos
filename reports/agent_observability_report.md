# Agent Mode Observability — Architecture Report

**Date:** 2026-06-17  
**Goal:** Expose real runtime telemetry in Agent Mode instead of relying on LLM narration.

---

## Before

```
User (Agent Mode)
    │
    ▼
POST /api/agent ──► CognitiveCycle.run(mode="agent")
    │                      │
    │                      ├─► CycleTrace (real UUID, duration_ms, stage flags)
    │                      ├─► cognitive_organs snapshots
    │                      └─► reasoning_integration flags
    │
    ▼
Response { reply, meta: { partial — 8 fields } }
    │
    ▼
frontend/index.html
    meta = null   ◄── DISCARDED
    │
    ▼
User sees ONLY data.reply (LLM prose)
    │
    └── Risk: LLM echoes [WORKING MEMORY] / invents cycle IDs, organ counts, durations
```

### Problems

| Issue | Location |
|-------|----------|
| Meta discarded | `frontend/index.html` — `meta = null` for agent |
| Partial agent meta | `backend/api/agent.py` — only 8 fields vs chat's 17+ |
| No Runtime Trace panel | Chat UI had stage tags only; no structured cycle_trace |
| LLM telemetry narration | No guard; reply could claim cycle IDs / organ counts |
| Identical meta contract | No shared builder; agent/chat diverged |

---

## After

```
User (Agent Mode)
    │
    ▼
POST /api/agent ──► CognitiveCycle.run(mode="agent")
    │                      │
    │                      ├─► CycleTrace (uuid, perf_counter durations)
    │                      ├─► apply_telemetry_narration_guard(reply)  ◄── NEW
    │                      └─► full result dict
    │
    ▼
build_runtime_meta(result)  ◄── SHARED with /api/chat
    │
    ▼
Response { reply, tool, meta: RUNTIME_META_KEYS (27 fields) }
    │
    ▼
frontend/index.html
    meta = data.meta   ◄── FIXED
    renderAiMetaPanels(meta)
    renderRuntimeTracePanel(meta)  ◄── NEW
    │
    ▼
User sees:
  • LLM answer (telemetry claims stripped)
  • Same tags/panels as Chat (quality, conf, stage_trace, simulation, meta-cog)
  • Runtime Trace panel (cycle_id, cycle_trace, organs, memory/belief influence, goal)
  • "Telemetry unavailable" per section when data missing — never inferred from reply
```

---

## Files changed

| File | Change |
|------|--------|
| `backend/api/meta.py` | **NEW** — `build_runtime_meta()`, `RUNTIME_META_KEYS` |
| `backend/api/chat.py` | Uses shared `build_runtime_meta()` |
| `backend/api/agent.py` | Full meta via `build_runtime_meta()` |
| `src/chetnaos/reasoning/honesty_guard.py` | Telemetry narration prompt rule + `apply_telemetry_narration_guard()` |
| `src/chetnaos/cycle/cognitive_cycle.py` | Strip telemetry from reply before return |
| `frontend/index.html` | Wire agent meta; `renderRuntimeTracePanel()`; shared `renderAiMetaPanels()` |
| `tests/test_agent_meta.py` | **NEW** — meta key parity test |

---

## Runtime meta contract (`RUNTIME_META_KEYS`)

Both `/api/chat` and `/api/agent` return identical keys:

`cycle`, `cycle_id`, `quality`, `confidence`, `confidence_level`, `dharma_score`, `cycle_score`, `domain`, `intent`, `beliefs_count`, `health`, `slept`, `stage_trace`, `cycle_trace`, `reality`, `simulation`, `meta_cognition`, `cognitive_organs`, `reasoning_integration`, `memory_influence`, `belief_influence`, `goal`, `goal_progress`, `belief_changes`, `contradiction_resolutions`, `honesty_guard_changes`, `agent_tool`

---

## Telemetry rules

1. **UI:** Runtime Trace reads only `meta` — never parses `reply`.
2. **Prompt:** Honesty guard instructs LLM not to narrate cycle IDs, durations, organ counts, timestamps.
3. **Post-process:** `apply_telemetry_narration_guard()` removes matching patterns from reply text.
4. **Missing data:** Frontend shows `Telemetry unavailable` — no estimates.

---

## Verification

```bash
python -m pytest tests/test_agent_meta.py -q
python scripts/phase7_gate.py
```

Expected: Agent and Chat meta key sets are identical; phase7 gate passes.
