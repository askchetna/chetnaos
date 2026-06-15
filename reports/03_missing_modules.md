# 03 — Missing Modules

**Analysis date:** 2026-06-15  
**Evidence basis:** Repository scan + cognitive component checklist vs implementation

Items marked **MISSING** have no dedicated module in the repository.  
Items marked **PARTIAL** exist but lack required cognitive depth.

---

## A. Scaffolded but Empty (files exist, zero bytes)

| Path | Expected Role (from README) | Status |
|------|----------------------------|--------|
| `backend/agents/chat_agent.py` | Chat agent | **EMPTY** |
| `backend/agents/intent_detecter.py` | Intent detection | **EMPTY** |
| `backend/agents/scheduler_agent.py` | Scheduling | **EMPTY** |
| `backend/agents/voice_agent.py` | Voice I/O | **EMPTY** |
| `backend/agents/whatsapp_agent.py` | WhatsApp agent | **EMPTY** |
| `backend/integrations/emailer.py` | Email | **EMPTY** |
| `backend/integrations/notifier.py` | Notifications | **EMPTY** |
| `backend/integrations/telecrm_api.py` | CRM | **EMPTY** |
| `backend/integrations/whatsapp_web.py` | WhatsApp web | **EMPTY** |
| `backend/workflows/followup_flow.py` | Follow-up automation | **EMPTY** |
| `backend/workflows/lead_flow.py` | Lead handling | **EMPTY** |
| `backend/workflows/meeting_flow.py` | Meeting flow | **EMPTY** |
| `src/chetnaos/main.py` | CLI entry | **EMPTY** |

---

## B. Cognitive Components — Missing Module Specs

### 1. Self Model

| Field | Value |
|-------|-------|
| **Status** | **MISSING** |
| **Filename** | `src/chetnaos/cognition/self_model.py` |
| **Class** | `SelfModel` |
| **Purpose** | Maintain explicit model of own capabilities, limits, and state — distinct from `Identity` (name/values) |
| **Inputs** | `development` stats, `skills` rankings, `meta_cognition` verdicts, `homeostasis` stress |
| **Outputs** | `capability_map`, `known_limits`, `confidence_in_self` |
| **Dependencies** | `identity`, `development`, `skills`, `meta_cognition`, `homeostasis` |

**Evidence:** `identity.py` stores name/values/tick counter. No module models "what I can/cannot do."

---

### 2. Episodic Memory (unified)

| Field | Value |
|-------|-------|
| **Status** | **PARTIAL** — `experience.py` + `experiences.jsonl` exist but no retrieval API in cycle |
| **Filename** | `src/chetnaos/memory/episodic_store.py` |
| **Class** | `EpisodicStore` |
| **Purpose** | Time-indexed episode storage with temporal retrieval (not just vector search) |
| **Inputs** | Experience records, timestamps, salience |
| **Outputs** | `recall_by_time()`, `recall_by_theme()`, episode chains |
| **Dependencies** | `experience`, `memory_hierarchy` |

**Evidence:** `Experience.record()` appends JSONL. `Memory.recall()` uses vector search only. Episodes not recalled in RECALL stage.

---

### 3. Semantic Memory (unified)

| Field | Value |
|-------|-------|
| **Status** | **PARTIAL** — scattered across `beliefs.json`, `lessons.jsonl`, vector DB |
| **Filename** | `src/chetnaos/memory/semantic_store.py` |
| **Class** | `SemanticStore` |
| **Purpose** | Consolidated factual/conceptual knowledge with provenance |
| **Inputs** | Beliefs, lessons, consolidated sleep output |
| **Outputs** | Queryable knowledge graph / fact store |
| **Dependencies** | `beliefs`, `learning`, `sleep`, `memory/db` |

---

### 4. Working Memory (controller)

| Field | Value |
|-------|-------|
| **Status** | **PARTIAL** — `memory_hierarchy.push_working()` only; no capacity/eviction policy |
| **Filename** | `src/chetnaos/memory/working_memory.py` |
| **Class** | `WorkingMemory` |
| **Purpose** | Bounded active context buffer with attention-weighted eviction |
| **Inputs** | Percept, attention weights, current goal |
| **Outputs** | Active context window for reasoning |
| **Dependencies** | `attention`, `memory_hierarchy` |

---

### 5. Belief Revision Engine

| Field | Value |
|-------|-------|
| **Status** | **PARTIAL** — `beliefs.update()` appends; no formal revision logic |
| **Filename** | `src/chetnaos/cognition/belief_revision.py` |
| **Class** | `BeliefRevisionEngine` |
| **Purpose** | Bayesian or rule-based belief update with evidence weighting |
| **Inputs** | New evidence, reflection quality, reality check |
| **Outputs** | Revised belief set with audit trail |
| **Dependencies** | `beliefs`, `reality`, `learning` |

---

### 6. Curiosity / Intrinsic Motivation

| Field | Value |
|-------|-------|
| **Status** | **MISSING** |
| **Filename** | `src/chetnaos/cognition/curiosity.py` |
| **Class** | `CuriosityDrive` |
| **Purpose** | Generate exploration goals from novelty, uncertainty, knowledge gaps |
| **Inputs** | `workspace_state` open questions, `meta_cognition`, domain coverage |
| **Outputs** | `exploration_goals`, `novelty_score` |
| **Dependencies** | `workspace_state`, `meta_cognition`, `self_trainer` |

**Evidence:** `play.py` does lightweight exploration. No curiosity drive or intrinsic reward.

---

### 7. Goal Management

| Field | Value |
|-------|-------|
| **Status** | **PARTIAL** — `purpose.py`, `self_trainer.py`; no goal queue/priority stack |
| **Filename** | `src/chetnaos/planning/goal_manager.py` |
| **Class** | `GoalManager` |
| **Purpose** | Multi-goal stack with priority, deferral, completion tracking |
| **Inputs** | User goals, training goals, founder mission |
| **Outputs** | Active goal, goal history, completion events |
| **Dependencies** | `purpose`, `self_trainer`, `founder_context` |

**Evidence:** `/api/goal` runs same cycle as chat with `mode="goal"` but no goal state machine.

---

### 8. Executive Controller

| Field | Value |
|-------|-------|
| **Status** | **PARTIAL** — `cognitive_cycle.py` is monolithic executive, not a separable controller |
| **Filename** | `src/chetnaos/cognition/executive.py` |
| **Class** | `ExecutiveController` |
| **Purpose** | Resource allocation, stage gating, interrupt handling, mode switching |
| **Inputs** | Cycle state, homeostasis alerts, user mode |
| **Outputs** | Stage schedule, skip/abort decisions |
| **Dependencies** | `state_machine`, `homeostasis`, `sleep_manager` |

---

### 9. Dharma Engine (unified)

| Field | Value |
|-------|-------|
| **Status** | **PARTIAL** — split across `constitution/*`, `reflection_v2`, `dharma_net` (orphaned) |
| **Filename** | `src/chetnaos/values/dharma_engine.py` |
| **Class** | `DharmaEngine` |
| **Purpose** | Single values/ethics enforcement layer with scoring |
| **Inputs** | Proposed action/text, context risk |
| **Outputs** | `dharma_score`, `violations`, `corrections` |
| **Dependencies** | `constitution`, `reflection_v2` |

---

### 10. Emotional Model

| Field | Value |
|-------|-------|
| **Status** | **MISSING** |
| **Filename** | `src/chetnaos/cognition/emotion.py` |
| **Class** | `EmotionalState` |
| **Purpose** | Affect representation influencing attention, risk tolerance, tone |
| **Inputs** | Interaction outcomes, homeostasis stress, relationship history |
| **Outputs** | `valence`, `arousal`, `tone_modifier` |
| **Dependencies** | `homeostasis`, `relationship`, `development` |

---

### 11. Social Learning

| Field | Value |
|-------|-------|
| **Status** | **MISSING** |
| **Filename** | `src/chetnaos/learning/social_learning.py` |
| **Class** | `SocialLearner` |
| **Purpose** | Learn from observed others' strategies and outcomes |
| **Inputs** | External demonstrations, civilization memory |
| **Outputs** | Adopted strategies, social norms |
| **Dependencies** | `civilization_memory`, `skills` |

---

### 12. Action Executor

| Field | Value |
|-------|-------|
| **Status** | **PARTIAL** — `embodiment.py` exists but `act()` never called; `backend/agent.py` is separate tool path |
| **Filename** | `src/chetnaos/action/executor.py` |
| **Class** | `ActionExecutor` |
| **Purpose** | Bridge cognitive output to real tools (web, calc, APIs) |
| **Inputs** | Decision output, tool registry |
| **Outputs** | Tool results, action log |
| **Dependencies** | `decision`, `backend/agent` tools |

---

### 13. Workspace Manager (unified)

| Field | Value |
|-------|-------|
| **Status** | **PARTIAL** — `workspace_state.py` persists JSON; `workspace.py` orphaned |
| **Filename** | `src/chetnaos/workspace/manager.py` |
| **Class** | `WorkspaceManager` |
| **Purpose** | Unified cognitive workspace: active artifacts, questions, focus |
| **Inputs** | Cycle outputs, contradictions |
| **Outputs** | Workspace snapshot for dashboard and reasoning |
| **Dependencies** | `workspace_state`, `artifacts`, `contradiction_tracker` |

---

### 14. Tests

| Field | Value |
|-------|-------|
| **Status** | **MISSING** |
| **Filename** | `tests/` directory |
| **Purpose** | Unit + integration tests for cognitive cycle |
| **Dependencies** | All modules |

---

## C. Summary Table

| Cognitive Component | Status |
|---------------------|--------|
| Identity | EXISTS (`identity.py`) |
| Self model | **MISSING** |
| Episodic memory | **PARTIAL** |
| Semantic memory | **PARTIAL** |
| Working memory | **PARTIAL** |
| Belief revision | **PARTIAL** |
| Contradiction handling | EXISTS (`contradiction_tracker`, `reality/contradiction_detector`) |
| Attention | EXISTS (`attention.py`) |
| Curiosity | **MISSING** |
| Planning | EXISTS (`planning.py`) |
| Goal management | **PARTIAL** |
| Executive controller | **PARTIAL** (monolithic cycle) |
| Simulation engine | EXISTS (`simulation.py`) |
| World model | EXISTS (`world_model.py`) — duplicate in backend |
| Founder model | EXISTS (`founder_context.py`) |
| Value system | EXISTS (`constitution/`) |
| Dharma engine | **PARTIAL** (split) |
| Reflection | EXISTS (`reflection.py` + `reflection_v2`) |
| Self training | EXISTS (`self_trainer.py`) |
| Reality verification | EXISTS (`reality/`) |
| Meta cognition | EXISTS (`meta_cognition.py`) |
| Emotional model | **MISSING** |
| Relationship model | EXISTS (`relationship.py`) |
| Social learning | **MISSING** |
| Skill acquisition | EXISTS (`skills.py`) |
| Action executor | **PARTIAL** |
| Sleep & consolidation | EXISTS (`sleep.py`, `sleep_manager.py`) |
| Workspace manager | **PARTIAL** |
| Multi-agent layer | **MISSING** (empty files) |
| Integrations | **MISSING** (empty files) |
| Workflows | **MISSING** (empty files) |
