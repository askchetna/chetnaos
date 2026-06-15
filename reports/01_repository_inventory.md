# 01 — Repository Inventory

**Analysis date:** 2026-06-15  
**Scope:** Full static scan of `ChetnaOS.v1` (93 Python files, 4,738 LOC excluding `.venv`)  
**Method:** AST parse, import graph extraction, file-system walk

---

## A. Top-Level Layout

```
ChetnaOS.v1/
├── backend/              # FastAPI app, legacy v1 core, orphaned AGI loop
├── src/chetnaos/         # v2 developmental cognitive organism (LIVE)
├── memory/               # SQLite vector store + JSON/JSONL persistence
├── reflection/           # Dharma reflection rules engine
├── kalpavriksha/         # Domain plugin (land/crop/ROI)
├── frontend/             # Static HTML/JS UI
├── tools/                # CLI utilities
├── reports/              # This analysis output
├── attached_assets/      # Pasted notes (non-code)
├── .agents/memory/       # Agent context docs
├── .github/workflows/    # CI
├── requirements.txt
├── Procfile
├── runtime.txt
├── smoke.ps1
└── README.md
```

---

## B. Python Module Inventory (by package)

### `backend/` — 10 modules (LIVE entry: `app.py`)

| File | LOC | Classes | Role | Status |
|------|-----|---------|------|--------|
| `app.py` | 209 | ChatRequest, GoalRequest | FastAPI entry, wires v2 runtime | **LIVE** |
| `agent.py` | 169 | — | Tool agent (calc, web, Groq chat) | **LIVE** |
| `api.py` | 89 | EvaluateRequest, ROIRequest, CropRequest | Kalpavriksha routes | **LIVE** |
| `config.py` | 41 | Settings | Env/config loader | **LIVE** |
| `chetna_core.py` | 47 | ChetnaCore | Legacy v1 kernel | **ORPHANED** |
| `memory.py` | 29 | Smriti | Legacy SQLite (`smriti` table) | **ORPHANED** |
| `dharma_net.py` | 12 | DharmaFilter | Keyword dharma filter | **ORPHANED** |
| `world_state.py` | 19 | WorldState | Time/energy/news dict | **ORPHANED** |
| `evolution_engine.py` | 14 | EvolutionEngine | Stub adapt() | **ORPHANED** |
| `__init__.py` | 2 | — | Version string | — |

### `backend/agi/` — 6 modules (entire package ORPHANED)

| File | LOC | Classes | Role |
|------|-----|---------|------|
| `loop.py` | 119 | — | Recursive goal loop |
| `goal_agent.py` | 26 | — | `execute_goal()` |
| `memory_service.py` | 67 | MemoryService | Dual Smriti + MemoryDB |
| `types.py` | 36 | Goal, LoopStep, LoopResult, StepReflection | Pydantic models |
| `world_model.py` | 19 | WorldModel | Adapter over `WorldState` |
| `__init__.py` | 7 | — | Exports |

### `backend/agents/` — 5 files (ALL EMPTY)

| File | Status |
|------|--------|
| `chat_agent.py` | **EMPTY PLACEHOLDER** |
| `intent_detecter.py` | **EMPTY PLACEHOLDER** |
| `scheduler_agent.py` | **EMPTY PLACEHOLDER** |
| `voice_agent.py` | **EMPTY PLACEHOLDER** |
| `whatsapp_agent.py` | **EMPTY PLACEHOLDER** |

### `backend/integrations/` — 4 files (ALL EMPTY)

`emailer.py`, `notifier.py`, `telecrm_api.py`, `whatsapp_web.py` — **EMPTY PLACEHOLDERS**

### `backend/workflows/` — 3 files (ALL EMPTY)

`followup_flow.py`, `lead_flow.py`, `meeting_flow.py` — **EMPTY PLACEHOLDERS**

### `src/chetnaos/orchestrator/` — 6 modules (LIVE)

| File | LOC | Classes | Role |
|------|-----|---------|------|
| `cognitive_cycle.py` | 395 | CognitiveCycle | 26-stage cycle orchestrator |
| `runtime.py` | 32 | ChetnaRuntime | Singleton facade |
| `state_machine.py` | 74 | CycleStage, StateMachine | Stage enum + history |
| `llm_router.py` | 45 | LLMRouter | Groq client wrapper |
| `sleep_manager.py` | 15 | SleepManager | Sleep scheduling |
| `__init__.py` | 5 | — | Exports ChetnaRuntime |

### `src/chetnaos/constitution/` — 7 modules (LIVE via Reasoning)

| File | Exports |
|------|---------|
| `__init__.py` | `CONSTITUTION` dict |
| `mission.py` | `MISSION` |
| `values.py` | `VALUES`, `VALUE_NAMES` |
| `ethics.py` | `ETHICS` |
| `compassion.py` | `COMPASSION` |
| `sovereignty.py` | `SOVEREIGNTY` |
| `founder_governance.py` | `FOUNDER_GOVERNANCE` |

### `src/chetnaos/organism/` — 35 modules (LIVE, wired by CognitiveCycle)

| Module | Class | Persistence |
|--------|-------|-------------|
| `existence.py` | Existence | In-memory cycle counter |
| `purpose.py` | Purpose | `memory/purpose.json` |
| `perception.py` | Perception | — |
| `attention.py` | Attention | — |
| `memory.py` | Memory | Wraps `memory/db.py` |
| `imagination.py` | Imagination | — |
| `play.py` | Play | — |
| `abstraction.py` | Abstraction | — |
| `world_model.py` | WorldModel | In-memory |
| `reasoning.py` | Reasoning | — |
| `planning.py` | Planning | — |
| `decision.py` | Decision | — |
| `embodiment.py` | Embodiment | — (instantiated, unused in cycle) |
| `habit.py` | Habit | `memory/habits.json` |
| `experience.py` | Experience | `memory/experiences.jsonl` |
| `reflection.py` | Reflection | Delegates to `reflection_v2` |
| `learning.py` | Learning | `memory/lessons.jsonl` |
| `beliefs.py` | Beliefs | `memory/beliefs.json` |
| `identity.py` | Identity | `memory/identity.json` |
| `development.py` | Development | `memory/development.json` |
| `homeostasis.py` | Homeostasis | — |
| `sleep.py` | Sleep | `memory/sleep_log.jsonl` |
| `relationship.py` | Relationship | `memory/relationships.json` |
| `artifacts.py` | Artifacts | `memory/artifacts.jsonl` |
| `civilization_memory.py` | CivilizationMemory | `memory/civilization.jsonl` |
| `founder_context.py` | FounderContext | `memory/founder_context.json` (referenced) |
| `simulation.py` | SimulationEngine | — |
| `meta_cognition.py` | MetaCognition | `memory/meta_cognition.jsonl` |
| `skills.py` | Skills | `memory/skills.json` |
| `workspace_state.py` | WorkspaceState | `memory/workspace_state.json` |
| `workspace.py` | Workspace | — (**ORPHANED**) |
| `contradiction_tracker.py` | ContradictionTracker | `memory/contradictions.json` |
| `memory_hierarchy.py` | MemoryHierarchy | `memory/mem_hierarchy.json` |
| `self_trainer.py` | SelfTrainer | `memory/training_goals.json` |
| `__init__.py` | — | Docstring only |

### `src/chetnaos/organism/reality/` — 7 modules (LIVE)

| Module | Class |
|--------|-------|
| `__init__.py` | RealityChecker |
| `confidence_engine.py` | ConfidenceEngine |
| `contradiction_detector.py` | ContradictionDetector |
| `evidence_engine.py` | EvidenceEngine |
| `truth_estimator.py` | TruthEstimator |
| `belief_validator.py` | BeliefValidator |
| `source_ranker.py` | SourceRanker (**instantiated, never called**) |

### Other packages

| Package | Files | Role |
|---------|-------|------|
| `memory/` | `db.py` (147 LOC, MemoryDB) | Vector SQLite store |
| `reflection/` | `reflection_v2.py` (89 LOC) | Dharma scoring |
| `kalpavriksha/` | 4 files | Agricultural domain tools |
| `tools/` | `memory_audit.py` | Standalone CLI |
| `src/chetnaos/main.py` | **EMPTY** | — |

---

## C. Non-Python Assets

### `memory/` data files (17)

`beliefs.json`, `identity.json`, `purpose.json`, `habits.json`, `development.json`, `relationships.json`, `skills.json`, `contradictions.json`, `workspace_state.json`, `mem_hierarchy.json`, `training_goals.json`, `experiences.jsonl`, `lessons.jsonl`, `artifacts.jsonl`, `civilization.jsonl`, `meta_cognition.jsonl`, `db.py`

### `reflection/`

`dharma_rules.json`, `reflection_v2.py`

### `frontend/`

`index.html`, `dashboard.html`, `app.js`, `kalpavriksha_ui/` (land, crop, roi pages)

---

## D. Runtime Entry Points (evidence)

| Entry | Evidence |
|-------|----------|
| `uvicorn backend.app:app` | `Procfile`, `README.md`, `smoke.ps1` |
| Cognitive runtime | `backend/app.py` → `src.chetnaos.orchestrator.runtime.ChetnaRuntime` |
| Agent tools | `backend/agent.py` router at `/api/agent` |
| Kalpavriksha | `backend/api.py` routes |

---

## E. README vs Reality Gap

README claims these exist and are integrated:

- `backend/agi/` — exists but **not wired** to `app.py`
- `backend/agents/` — **13 empty files**, zero implementation
- `backend/integrations/` — **empty**
- `backend/workflows/` — **empty**

The **live** architecture is `src/chetnaos/` v2 cognitive organism, not the README's v0.9 AGI loop.

---

## F. Test Coverage

**MISSING** — No `tests/` directory. No pytest/unittest files in repository (excluding `.venv`).
