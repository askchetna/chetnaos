---
name: ChetnaOS Architecture
description: Full cognitive architecture layout, import paths, and key design decisions for ChetnaOS v2.0
---

## Architecture

ChetnaOS is a Developmental Cognitive Architecture (Level 6). One `CognitiveCycle` instance lives per process.

### Layers
- `src/chetnaos/constitution/` — Immutable values, ethics, mission (loaded at import time)
- `src/chetnaos/organism/` — 26 cognitive modules (one per stage)
- `src/chetnaos/organism/reality/` — Reality check layer (6 sub-modules)
- `src/chetnaos/orchestrator/` — LLM router, state machine, cognitive cycle, runtime

### Entry point
`from src.chetnaos.orchestrator.runtime import ChetnaRuntime` then `.process(text, mode)` returns full cycle result dict.

### 27-Stage Cycle (locked)
EXIST → PURPOSE → OBSERVE → ATTEND → RECALL → PREDICT → IMAGINE → PLAY → PLAN → HABIT → ACT → WORLD_UPDATE → EXPERIENCE → REALITY_CHECK → EVALUATE → FAILURE_RECOVERY → REFLECT → SELF_QUESTION → UPDATE_BELIEFS → UPDATE_IDENTITY → REFINE_PURPOSE → SLEEP → FORGET → CONSOLIDATE → WAKE

### LLM calls happen at
- IMAGINE (complex inputs only)
- PLAN (complex inputs only)
- ACT = Reasoning.reason() — primary call, always

### Persistent memory files (JSON/JSONL in memory/)
beliefs.json, identity.json, purpose.json, habits.json, experiences.jsonl, lessons.jsonl, development.json, sleep_log.jsonl, civilization.jsonl, relationships.json

### API routes
- POST /api/chat → chat mode (full cognitive cycle)
- POST /api/goal → goal mode (same cycle, goal framing)
- GET  /api/state → live identity/beliefs/world state
- GET  /health → system health + LLM availability

**Why:** Single-process singleton is the right pattern here — the organism has continuous state across requests (beliefs, identity, world model). Do not re-instantiate CognitiveCycle per request.

**How to apply:** `get_runtime()` from orchestrator/runtime.py returns the singleton. backend/app.py calls this lazily on startup.
