# 10 — Build Order

**Analysis date:** 2026-06-15  
**Principle:** Build bottom-up. Each layer depends only on layers below. No layer may import from above.

---

## A. Dependency Layers (build order)

```
Layer 0: values, tools                    (zero internal deps)
Layer 1: memory.store                     (depends: Layer 0)
Layer 2: memory subsystems                (depends: Layer 1)
Layer 3: cognition primitives             (depends: Layer 0, 1)
Layer 4: identity, world_model, reality   (depends: Layer 1, 3)
Layer 5: planning, simulation, learning   (depends: Layer 3, 4)
Layer 6: action, workspace, meta_cognition (depends: Layer 3, 4, 5)
Layer 7: organism (homeostasis, sleep)    (depends: Layer 2, 6)
Layer 8: executive + cognitive_cycle      (depends: ALL below)
Layer 9: runtime + app                    (depends: Layer 8)
```

---

## B. Module Build Order (54 steps)

### Layer 0 — Foundation (no internal dependencies)

| Step | Module | File | Source |
|------|--------|------|--------|
| 0.1 | Constitution | `values/constitution.py` | Merge `constitution/*` |
| 0.2 | DharmaEngine | `values/dharma_engine.py` | Port `reflection_v2.py` |
| 0.3 | Calculator | `tools/calculator.py` | Extract from `agent.py` |
| 0.4 | WebSearch | `tools/web_search.py` | Extract from `agent.py` |
| 0.5 | WebFetch | `tools/web_fetch.py` | Extract from `agent.py` |
| 0.6 | Config | `infrastructure/config.py` | Port `backend/config.py` |
| 0.7 | LLMRouter | `infrastructure/llm_router.py` | Port `orchestrator/llm_router.py` |
| 0.8 | StateMachine | `infrastructure/state_machine.py` | Port as-is |

### Layer 1 — Memory Core

| Step | Module | File | Depends On |
|------|--------|------|------------|
| 1.1 | MemoryStore | `memory/store.py` | 0.6 — **FIX upsert/recent API** |
| 1.2 | Test: memory store | `tests/test_memory_store.py` | 1.1 |

### Layer 2 — Memory Subsystems

| Step | Module | File | Depends On |
|------|--------|------|------------|
| 2.1 | WorkingMemory | `memory/working_memory.py` | 1.1 |
| 2.2 | EpisodicStore | `memory/episodic.py` | 1.1 — port `experience.py` |
| 2.3 | SemanticStore | `memory/semantic.py` | 1.1 — port `beliefs.py` |
| 2.4 | ProceduralStore | `memory/procedural.py` | 1.1 — port `skills.py`, `habit.py` |
| 2.5 | MemoryHierarchy | `memory/hierarchy.py` | 2.1 — port `memory_hierarchy.py` |
| 2.6 | ConsolidationEngine | `memory/consolidation.py` | 2.2, 2.3 — port `sleep.py` |

### Layer 3 — Cognition Primitives

| Step | Module | File | Depends On |
|------|--------|------|------------|
| 3.1 | Perception | `cognition/perception.py` | — |
| 3.2 | Attention | `cognition/attention.py` | 3.1 |
| 3.3 | Abstraction | `cognition/abstraction.py` | 3.1, 3.2 |
| 3.4 | Imagination | `cognition/imagination.py` | 0.7 |
| 3.5 | Play | `cognition/play.py` | 3.2 |
| 3.6 | Reasoning | `cognition/reasoning.py` | 0.1, 0.7 |
| 3.7 | Decision | `cognition/decision.py` | 3.6 |
| 3.8 | EmotionalState | `cognition/emotion.py` | NEW |
| 3.9 | CuriosityDrive | `cognition/curiosity.py` | NEW |
| 3.10 | SelfModel | `cognition/self_model.py` | NEW |

### Layer 4 — Identity, World, Reality

| Step | Module | File | Depends On |
|------|--------|------|------------|
| 4.1 | Identity | `identity/identity.py` | 2.3 |
| 4.2 | BeliefRevisionEngine | `identity/belief_revision.py` | 2.3, 0.2 — NEW |
| 4.3 | FounderModel | `identity/founder_model.py` | 2.3 — port `founder_context.py` |
| 4.4 | WorldModelEngine | `world_model/engine.py` | — port `world_model.py` |
| 4.5 | ConfidenceEngine | `reality/confidence.py` | — |
| 4.6 | EvidenceEngine | `reality/evidence.py` | — |
| 4.7 | TruthEstimator | `reality/truth.py` | 4.5, 4.6 |
| 4.8 | BeliefValidator | `reality/belief_validator.py` | 2.3 |
| 4.9 | ContradictionEngine | `reality/contradiction.py` | 2.3 — merge detector + tracker |
| 4.10 | SourceRanker | `reality/source_ranker.py` | — |
| 4.11 | RealityChecker | `reality/checker.py` | 4.5–4.10 |
| 4.12 | Test: reality | `tests/test_reality_checker.py` | 4.11 |

### Layer 5 — Planning, Simulation, Learning

| Step | Module | File | Depends On |
|------|--------|------|------------|
| 5.1 | Purpose | `planning/purpose.py` | 2.3 |
| 5.2 | GoalManager | `planning/goal_manager.py` | 5.1 — NEW |
| 5.3 | Planner | `planning/planner.py` | 0.7 |
| 5.4 | SimulationEngine | `simulation/engine.py` | 0.7 — port `simulation.py` |
| 5.5 | Learner | `learning/learner.py` | 2.3 — port `learning.py` |
| 5.6 | Skills | `learning/skills.py` | 2.4 |
| 5.7 | SelfTrainer | `learning/self_trainer.py` | 5.6 |
| 5.8 | SocialLearner | `learning/social_learning.py` | 5.6 — NEW |

### Layer 6 — Action, Workspace, Meta-Cognition

| Step | Module | File | Depends On |
|------|--------|------|------------|
| 6.1 | ToolRegistry | `agents/registry.py` | 0.3–0.5 |
| 6.2 | ActionExecutor | `action/executor.py` | 3.7, 6.1 — NEW |
| 6.3 | Embodiment | `action/embodiment.py` | 3.7 |
| 6.4 | WorkspaceManager | `workspace/manager.py` | 2.1 — port `workspace_state.py` |
| 6.5 | Artifacts | `workspace/artifacts.py` | 2.2 |
| 6.6 | Reflection | `meta_cognition/reflection.py` | 0.2 |
| 6.7 | MetaEvaluator | `meta_cognition/evaluator.py` | 6.6 — port `meta_cognition.py` |
| 6.8 | ChatAgent | `agents/chat.py` | 6.1, 0.7 — port `agent.py` |

### Layer 7 — Organism Regulation

| Step | Module | File | Depends On |
|------|--------|------|------------|
| 7.1 | Existence | `organism/existence.py` | — |
| 7.2 | Development | `organism/development.py` | 6.6 |
| 7.3 | Homeostasis | `organism/homeostasis.py` | 7.2 |
| 7.4 | SleepScheduler | `organism/sleep_scheduler.py` | 2.6 |

### Layer 8 — Executive & Cycle

| Step | Module | File | Depends On |
|------|--------|------|------------|
| 8.1 | ExecutiveController | `cognition/executive.py` | 7.3, 0.8 — NEW |
| 8.2 | CognitiveCycle | `infrastructure/cognitive_cycle.py` | ALL Layer 3–7 |
| 8.3 | Test: cycle | `tests/test_cognitive_cycle.py` | 8.2 |
| 8.4 | Test: dharma | `tests/test_dharma_engine.py` | 0.2 |

### Layer 9 — Runtime & Deployment

| Step | Module | File | Depends On |
|------|--------|------|------------|
| 9.1 | ChetnaRuntime | `infrastructure/runtime.py` | 8.2 |
| 9.2 | FastAPI App | `infrastructure/app.py` | 9.1, 6.8 |
| 9.3 | Kalpavriksha routes | `infrastructure/plugins/kalpavriksha/routes.py` | plugins |
| 9.4 | pyproject.toml | root | 9.1 |
| 9.5 | Update Procfile | root | 9.2 |
| 9.6 | Smoke test pass | `scripts/smoke.ps1` | 9.2 |

---

## C. Critical Path

The minimum viable rebuild path (fastest to working organism):

```
0.1 Constitution
0.2 DharmaEngine
1.1 MemoryStore (FIXED)
3.1 Perception → 3.2 Attention → 3.6 Reasoning → 3.7 Decision
4.11 RealityChecker
6.6 Reflection
8.2 CognitiveCycle (slim, using ported modules)
9.1 Runtime → 9.2 App
```

**11 modules** to get a working system. Everything else is enhancement.

---

## D. Parallel Workstreams

These can be built concurrently after Layer 1 is complete:

| Stream | Modules | Owner Focus |
|--------|---------|-------------|
| A: Memory | 2.1–2.6 | Data persistence |
| B: Cognition | 3.1–3.10 | Perception/reasoning |
| C: Reality | 4.5–4.12 | Grounding |
| D: Planning | 5.1–5.8 | Goals/simulation |
| E: Action | 6.1–6.8 | Tools/agents |
| F: Infrastructure | 9.1–9.6 | Deployment |

**Merge point:** Layer 8 (CognitiveCycle) requires all streams complete.

---

## E. New Module Build Specs (Layer 3+)

### `cognition/executive.py` — ExecutiveController

| Field | Value |
|-------|-------|
| **Class** | `ExecutiveController` |
| **Purpose** | Stage scheduling, LLM gating, interrupt on homeostasis critical |
| **Inputs** | `CycleStage`, homeostasis state, abstraction complexity |
| **Outputs** | `should_run(stage)`, `use_llm(stage)`, `skip_reason` |
| **Dependencies** | `state_machine`, `homeostasis` |
| **Build step** | 8.1 |

### `cognition/self_model.py` — SelfModel

| Field | Value |
|-------|-------|
| **Class** | `SelfModel` |
| **Purpose** | Track own capabilities and limits |
| **Inputs** | skills rankings, development stats, meta-cognition verdicts |
| **Outputs** | `capability_map`, `known_limits`, `self_confidence` |
| **Dependencies** | `learning/skills`, `organism/development`, `meta_cognition/evaluator` |
| **Build step** | 3.10 |

### `cognition/curiosity.py` — CuriosityDrive

| Field | Value |
|-------|-------|
| **Class** | `CuriosityDrive` |
| **Purpose** | Generate intrinsic exploration goals |
| **Inputs** | workspace open questions, domain coverage, novelty signals |
| **Outputs** | `exploration_goals`, `novelty_score` |
| **Dependencies** | `workspace/manager`, `planning/goal_manager` |
| **Build step** | 3.9 |

### `cognition/emotion.py` — EmotionalState

| Field | Value |
|-------|-------|
| **Class** | `EmotionalState` |
| **Purpose** | Affect model influencing tone and risk tolerance |
| **Inputs** | cycle quality, homeostasis stress, relationship history |
| **Outputs** | `valence`, `arousal`, `tone_modifier` |
| **Dependencies** | `organism/homeostasis`, `memory/episodic` |
| **Build step** | 3.8 |

### `identity/belief_revision.py` — BeliefRevisionEngine

| Field | Value |
|-------|-------|
| **Class** | `BeliefRevisionEngine` |
| **Purpose** | Evidence-weighted belief updates with audit trail |
| **Inputs** | new evidence, reflection quality, reality confidence |
| **Outputs** | revised beliefs, revision log |
| **Dependencies** | `memory/semantic`, `values/dharma_engine`, `reality/checker` |
| **Build step** | 4.2 |

### `planning/goal_manager.py` — GoalManager

| Field | Value |
|-------|-------|
| **Class** | `GoalManager` |
| **Purpose** | Multi-goal stack with priority and completion |
| **Inputs** | user goals, training goals, founder mission |
| **Outputs** | `active_goal`, `goal_queue`, `completion_events` |
| **Dependencies** | `planning/purpose`, `learning/self_trainer`, `identity/founder_model` |
| **Build step** | 5.2 |

### `action/executor.py` — ActionExecutor

| Field | Value |
|-------|-------|
| **Class** | `ActionExecutor` |
| **Purpose** | Execute tool calls from cognitive decisions |
| **Inputs** | decision output, tool registry |
| **Outputs** | tool results, action log |
| **Dependencies** | `cognition/decision`, `agents/registry` |
| **Build step** | 6.2 |

### `learning/social_learning.py` — SocialLearner

| Field | Value |
|-------|-------|
| **Class** | `SocialLearner` |
| **Purpose** | Learn strategies from external/civilization memory |
| **Inputs** | civilization contributions, external demonstrations |
| **Outputs** | adopted strategies |
| **Dependencies** | `memory/episodic`, `learning/skills` |
| **Build step** | 5.8 |

### `memory/working_memory.py` — WorkingMemory

| Field | Value |
|-------|-------|
| **Class** | `WorkingMemory` |
| **Purpose** | Bounded active context with attention-weighted eviction |
| **Inputs** | percept, attention weights, capacity limit |
| **Outputs** | active context window |
| **Dependencies** | `cognition/attention`, `memory/store` |
| **Build step** | 2.1 |

---

## F. Verification Checklist (per layer)

| Layer | Verification |
|-------|-------------|
| 0 | `from chetnaos.values.constitution import CONSTITUTION` loads |
| 1 | `MemoryStore.upsert()` + `search()` + `recent()` pass tests |
| 2 | Episodic write → recall returns same episode |
| 3 | Perception → Reasoning pipeline produces response |
| 4 | RealityChecker returns confidence on sample text |
| 5 | Planner + Simulation produce 3 plans |
| 6 | ActionExecutor runs calculator tool |
| 7 | Sleep consolidates beliefs (prune < 0.3) |
| 8 | Full cycle `run("hello")` returns reply dict |
| 9 | `uvicorn` serves `/health`, `/api/chat`, `/api/dashboard` |

---

## G. Estimated Effort

| Phase | Steps | New Modules | Ported Modules | Effort |
|-------|-------|-------------|----------------|--------|
| Phase 1 | 0.1–1.2 | 0 | 2 fixes | 2–3 days |
| Phase 2 | 2.1–2.6, 0.1–0.2 | 2 | 8 | 1 week |
| Phase 3 | 3–9 | 9 | 35 | 2–3 weeks |
| Phase 4 | Tests + hardening | 0 | 0 | 1–2 weeks |
| **Total** | **54 steps** | **9 new** | **45 ported** | **6–8 weeks** |
