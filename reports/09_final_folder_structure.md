# 09 — Final Folder Structure

**Analysis date:** 2026-06-15  
**Target:** Post-Phase 4 repository layout

---

## A. Complete Repository Tree

```
ChetnaOS/
│
├── chetnaos/                          # Single Python package (replaces src/chetnaos + backend cognition)
│   │
│   ├── organism/                      # Lifecycle & regulation
│   │   ├── __init__.py
│   │   ├── existence.py               # ← organism/existence.py
│   │   ├── development.py             # ← organism/development.py
│   │   ├── homeostasis.py             # ← organism/homeostasis.py
│   │   └── sleep_scheduler.py         # ← orchestrator/sleep_manager.py
│   │
│   ├── cognition/                       # Perception → reasoning
│   │   ├── __init__.py
│   │   ├── perception.py              # ← organism/perception.py
│   │   ├── attention.py               # ← organism/attention.py
│   │   ├── abstraction.py             # ← organism/abstraction.py
│   │   ├── imagination.py             # ← organism/imagination.py
│   │   ├── play.py                    # ← organism/play.py
│   │   ├── reasoning.py               # ← organism/reasoning.py
│   │   ├── decision.py                # ← organism/decision.py
│   │   ├── executive.py               # NEW — extracted from cognitive_cycle
│   │   ├── self_model.py              # NEW
│   │   ├── curiosity.py               # NEW
│   │   └── emotion.py                 # NEW
│   │
│   ├── memory/                          # Unified memory
│   │   ├── __init__.py
│   │   ├── store.py                   # ← memory/db.py + organism/memory.py
│   │   ├── working_memory.py          # NEW — ← organism/memory_hierarchy (working part)
│   │   ├── episodic.py                # ← organism/experience.py
│   │   ├── semantic.py                # ← organism/beliefs.py + learning.py
│   │   ├── procedural.py              # ← organism/skills.py + habit.py
│   │   ├── hierarchy.py               # ← organism/memory_hierarchy.py
│   │   └── consolidation.py           # ← organism/sleep.py
│   │
│   ├── identity/                        # Self-representation
│   │   ├── __init__.py
│   │   ├── identity.py                # ← organism/identity.py
│   │   ├── beliefs.py                 # ← organism/beliefs.py (facade)
│   │   ├── belief_revision.py         # NEW
│   │   └── founder_model.py           # ← organism/founder_context.py
│   │
│   ├── values/                          # Constitution & dharma
│   │   ├── __init__.py
│   │   ├── constitution.py            # ← constitution/* merged
│   │   ├── dharma_engine.py             # ← reflection/reflection_v2.py
│   │   └── rules/
│   │       └── dharma_rules.json        # ← reflection/dharma_rules.json
│   │
│   ├── world_model/                     # External state
│   │   ├── __init__.py
│   │   └── engine.py                    # ← organism/world_model.py
│   │
│   ├── simulation/                      # Mental rehearsal
│   │   ├── __init__.py
│   │   └── engine.py                    # ← organism/simulation.py
│   │
│   ├── planning/                        # Goals & plans
│   │   ├── __init__.py
│   │   ├── planner.py                   # ← organism/planning.py
│   │   ├── goal_manager.py              # NEW
│   │   └── purpose.py                   # ← organism/purpose.py
│   │
│   ├── action/                          # Motor output
│   │   ├── __init__.py
│   │   ├── executor.py                  # NEW
│   │   └── embodiment.py                # ← organism/embodiment.py
│   │
│   ├── learning/                        # Adaptation
│   │   ├── __init__.py
│   │   ├── learner.py                   # ← organism/learning.py
│   │   ├── skills.py                    # ← organism/skills.py
│   │   ├── self_trainer.py              # ← organism/self_trainer.py
│   │   └── social_learning.py           # NEW
│   │
│   ├── meta_cognition/                  # Self-monitoring
│   │   ├── __init__.py
│   │   ├── evaluator.py                 # ← organism/meta_cognition.py
│   │   └── reflection.py                # ← organism/reflection.py
│   │
│   ├── reality/                         # Grounding
│   │   ├── __init__.py                  # RealityChecker
│   │   ├── checker.py                   # ← organism/reality/__init__.py
│   │   ├── confidence.py                # ← confidence_engine.py
│   │   ├── evidence.py                  # ← evidence_engine.py
│   │   ├── truth.py                     # ← truth_estimator.py
│   │   ├── belief_validator.py          # ← belief_validator.py
│   │   ├── contradiction.py             # ← contradiction_detector + contradiction_tracker
│   │   └── source_ranker.py             # ← source_ranker.py
│   │
│   ├── agents/                          # Agent layer
│   │   ├── __init__.py
│   │   ├── chat.py                      # ← backend/agent.py (refactored)
│   │   └── registry.py                  # NEW — tool registry
│   │
│   ├── tools/                           # External tools
│   │   ├── __init__.py
│   │   ├── calculator.py                # ← extracted from agent.py
│   │   ├── web_search.py                # ← extracted from agent.py
│   │   └── web_fetch.py                 # ← extracted from agent.py
│   │
│   ├── workspace/                       # Cognitive workspace
│   │   ├── __init__.py
│   │   ├── manager.py                   # ← organism/workspace_state.py
│   │   └── artifacts.py                 # ← organism/artifacts.py
│   │
│   └── infrastructure/                  # Deployment shell
│       ├── __init__.py
│       ├── app.py                       # ← backend/app.py
│       ├── config.py                    # ← backend/config.py
│       ├── runtime.py                   # ← orchestrator/runtime.py
│       ├── cognitive_cycle.py           # ← orchestrator/cognitive_cycle.py (slimmed)
│       ├── state_machine.py             # ← orchestrator/state_machine.py
│       ├── llm_router.py                # ← orchestrator/llm_router.py
│       └── plugins/
│           └── kalpavriksha/            # ← kalpavriksha/* (domain plugin)
│               ├── __init__.py
│               ├── evaluator.py
│               ├── roi.py
│               └── crop_planner.py
│
├── data/                                # Runtime persistence (renamed from memory/)
│   ├── mem.db                           # SQLite vector store
│   ├── beliefs.json
│   ├── identity.json
│   ├── purpose.json
│   ├── habits.json
│   ├── skills.json
│   ├── development.json
│   ├── relationships.json
│   ├── contradictions.json
│   ├── workspace_state.json
│   ├── mem_hierarchy.json
│   ├── training_goals.json
│   ├── founder_context.json
│   ├── experiences.jsonl
│   ├── lessons.jsonl
│   ├── artifacts.jsonl
│   ├── civilization.jsonl
│   ├── meta_cognition.jsonl
│   └── sleep_log.jsonl
│
├── frontend/                            # Static UI (unchanged)
│   ├── index.html
│   ├── dashboard.html
│   ├── app.js
│   └── kalpavriksha_ui/
│
├── tests/                               # NEW
│   ├── conftest.py
│   ├── test_memory_store.py
│   ├── test_cognitive_cycle.py
│   ├── test_dharma_engine.py
│   ├── test_reality_checker.py
│   └── test_goal_manager.py
│
├── scripts/                             # Operational scripts
│   ├── memory_audit.py                  # ← tools/memory_audit.py
│   └── smoke.ps1                        # ← smoke.ps1
│
├── reports/                             # Architecture analysis (this set)
│
├── .github/workflows/ci.yml
├── pyproject.toml                       # NEW — package definition
├── requirements.txt
├── Procfile
├── runtime.txt
├── env.example
├── README.md
└── SETUP.md
```

---

## B. Deleted in Final State

```
DELETED (no replacement):
  backend/agi/
  backend/chetna_core.py
  backend/memory.py (Smriti)
  backend/dharma_net.py
  backend/world_state.py
  backend/evolution_engine.py
  backend/agents/ (all empty)
  backend/integrations/ (all empty)
  backend/workflows/ (all empty)
  src/chetnaos/ (after shim period)
  backend/ (after move to infrastructure/)
  memory/db.py (moved to chetnaos/memory/store.py)
  reflection/ (moved to chetnaos/values/)
  kalpavriksha/ (moved to plugins/)
  organism/workspace.py
  tools/ (moved to scripts/)
```

---

## C. Mapping: Current → Target

| Current Path | Target Path |
|-------------|-------------|
| `src/chetnaos/organism/*.py` | `chetnaos/{cognition,memory,identity,...}/` |
| `src/chetnaos/orchestrator/*.py` | `chetnaos/infrastructure/` |
| `src/chetnaos/constitution/*.py` | `chetnaos/values/constitution.py` |
| `backend/app.py` | `chetnaos/infrastructure/app.py` |
| `backend/config.py` | `chetnaos/infrastructure/config.py` |
| `backend/agent.py` | `chetnaos/agents/chat.py` + `chetnaos/tools/` |
| `backend/api.py` | `chetnaos/infrastructure/plugins/kalpavriksha/routes.py` |
| `memory/db.py` | `chetnaos/memory/store.py` |
| `memory/*.json` | `data/*.json` |
| `reflection/reflection_v2.py` | `chetnaos/values/dharma_engine.py` |
| `reflection/dharma_rules.json` | `chetnaos/values/rules/dharma_rules.json` |
| `kalpavriksha/*` | `chetnaos/infrastructure/plugins/kalpavriksha/` |

---

## D. Procfile (target)

```
web: uvicorn chetnaos.infrastructure.app:app --host 0.0.0.0 --port $PORT
```

---

## E. pyproject.toml (target skeleton)

```toml
[project]
name = "chetnaos"
version = "3.0.0"
requires-python = ">=3.11"

[tool.setuptools.packages.find]
where = ["."]
include = ["chetnaos*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```
