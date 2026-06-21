# Discourse Layer v3 Report

**Date:** 2026-06-21  
**Focus:** Conversational intelligence upgrade — audience, goals, knowledge ordering, pragmatics, self-monitor

---

## What Changed (v2 → v3)

| Area | v2 | v3 |
|------|----|----|
| Audience | Implicit via intent | **`audience_model.py`** — beginner, expert, programmer, founder, researcher, casual |
| Response goal | Intent-only schemas | **`response_goal_engine.py`** — explain, teach, debug, compare, plan, brainstorm, comfort, decide, clarify |
| Knowledge order | `response_planner.py` | **`knowledge_planner.py`** — goal-driven section ordering (Applications, Objective, etc.) |
| Hidden intent | Dialogue acts only | **`pragmatics_engine.py`** — frustration, confusion, agreement, delegation, urgency |
| Final QA | `quality_goals.py` only | **`self_monitor.py`** — repetition, certainty, founder mentions, debug steps |
| Pipeline | 8 stages | **12 stages** (see below) |

---

## Files Added (v3)

| File | Role |
|------|------|
| `audience_model.py` | Rule-based audience inference + adaptation hints |
| `response_goal_engine.py` | Primary response goal from intent + pragmatics |
| `knowledge_planner.py` | Goal-driven knowledge section ordering |
| `pragmatics_engine.py` | Hidden intent (Hinglish frustration, confusion, agreement) |
| `self_monitor.py` | Pre-delivery quality pass (never exposed to user) |

## Files Updated

| File | Change |
|------|--------|
| `answer_composer.py` | v3 orchestrator — full 12-stage pipeline |
| `context_awareness.py` | Added `frustration`, `urgency` dialogue acts |
| `response_planner.py` | Thin wrapper delegating to `knowledge_planner` |
| `conversation_patterns.py` | v3 schemas (`applications`, `objective`) |
| `__init__.py` | Exports v3 modules |

## Test Files Added

| File | Tests |
|------|-------|
| `tests/test_audience_model.py` | 9 |
| `tests/test_response_goal_engine.py` | 9 |
| `tests/test_knowledge_planner.py` | 9 |
| `tests/test_pragmatics_engine.py` | 9 |
| `tests/test_self_monitor.py` | 9 |
| `tests/test_discourse_layer.py` | 18 (updated for v3) |

---

## v3 Pipeline

```
Reasoning (unchanged)
    ↓
IntentClassifier
    ↓
ContextAwareness
    ↓
PragmaticsEngine
    ↓
AudienceModel
    ↓
ResponseGoalEngine
    ↓
KnowledgePlanner (+ ConversationPatterns)
    ↓
Answer composition (structure)
    ↓
ToneEngine
    ↓
LanguageStyleEngine
    ↓
QualityGoals
    ↓
SelfMonitor
    ↓
ResponseComposer (unchanged)
```

---

## Integration Point (unchanged architecture)

Single hook in `cognitive_cycle.py` after reasoning, before final compose:

```python
discourse_reply = DiscourseLayer.transform(
    user_input, final_output, conversation_context=conversation_context,
)
composed_reply = ResponseComposer.compose(discourse_reply)
```

**Removable:** Delete the two lines above and import; no other system changes required.

---

## v3 Knowledge Schemas

**Learning / Explain:** Definition → Intuition → Example → Applications → Summary  
**Decision:** Goal → Options → Tradeoffs → Recommendation → Reason  
**Planning:** Objective → Priorities → Steps → Risks → Next action  
**Debug:** Observation → Cause → Fix → Verification  
**Identity:** Introduction → Purpose → Capabilities → Invitation  

---

## Audience Adaptation

| Audience | Behavior |
|----------|----------|
| Beginner | Simple language, short sentences |
| Expert | More technical depth, structured |
| Programmer | Code-first ordering |
| Founder | Strategy + tradeoffs + execution focus |
| Researcher | Methodology and evidence framing |
| Casual user | Warm, concise, low jargon |

---

## Pragmatics Examples

| User input | Hidden intent | Response behavior |
|------------|---------------|-------------------|
| "Ye sab mujhse nahi hoga" | frustration + simplify | Acknowledge difficulty; simplify |
| "Samjha nahi" | confusion | "Koi baat nahi. Main aur simple tareeke se samjhata hoon." |
| "Achha" | agreement | Short reply; no over-explanation |
| "tum kar do yeh kaam" | delegation | Practical, action-oriented |
| "This is urgent fix now" | urgency | Shorter, prioritized answer |

---

## Before / After Examples

### Frustration — "Ye sab mujhse nahi hoga"

**Before (v2):** Raw reasoning output repeated without acknowledgment.  
**After (v3):** Prefix acknowledges difficulty and offers simplified path; verbosity forced short.

### Confusion — "Samjha nahi"

**Before (v2):** Generic emotional template appended to long answer.  
**After (v3):** Returns pragmatic prefix only — clear, warm, no repetition.

### Agreement — "Achha"

**Before (v2):** Full structured reply to a one-word ack.  
**After (v3):** "Theek hai. Agla step batao jab ready ho."

### Programmer — coding question

**Before (v2):** Code block sometimes buried in prose.  
**After (v3):** Audience model sets `code_first`; knowledge planner puts code block first.

### Founder — strategy question

**Before (v2):** Same depth as casual queries.  
**After (v3):** Structured plan schema with objective, tradeoffs, next action.

### Self-monitor — overconfident draft

**Before:** "Certainly! This will definitely work 100%."  
**After:** "This will likely work likely." (robotic openers stripped, certainty softened)

---

## Architecture Confirmation

| Component | Status |
|-----------|--------|
| HTTP APIs | **Unchanged** |
| Frontend | **Unchanged** |
| Memory subsystem | **Unchanged** |
| Cognitive cycle (27 stages) | **Unchanged** (same 2-line discourse hook) |
| Prompt builder | **Unchanged** |
| Reasoning engine | **Unchanged** |
| ResponseComposer | **Unchanged** (final sanitize only) |

---

## Test Results

```
tests/test_audience_model.py         9 passed
tests/test_response_goal_engine.py   9 passed
tests/test_knowledge_planner.py      9 passed
tests/test_pragmatics_engine.py      9 passed
tests/test_self_monitor.py           9 passed
tests/test_discourse_layer.py       18 passed
----------------------------------------
Discourse suite                     63 passed
Full suite                         178 passed
```

Target of **150+ passing tests: met.**

---

## Language & Quality Rules (enforced)

- Natural Hinglish; warm and respectful
- Avoid: organism, entity, jeev, janwar, heavy Sanskrit, robotic openers
- No fake emotions; minimal emojis
- Founder mentions only when user asks
- Priority: **Correctness > clarity > helpfulness > elegance**

---

## Removability

The entire v3 layer lives under `src/chetnaos/discourse/`. To disable:

1. Remove `DiscourseLayer.transform(...)` call in `cognitive_cycle.py`
2. Pass `final_output` directly to `ResponseComposer.compose()`

No API contracts, memory schemas, or cycle stage definitions depend on discourse modules.
