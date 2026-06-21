# Discourse Layer Upgrade Report

**Date:** 2026-06-21  
**Goal:** Improve response quality, structure, and naturalness without changing APIs, memory, cognitive cycle architecture, or frontend.

---

## Summary

Added a lightweight **Discourse Layer** between reasoning output and `ResponseComposer`. The cognitive cycle, HTTP APIs, memory subsystem, and frontend are unchanged except for **one additive hook** (2 lines) in `cognitive_cycle.py`.

---

## Files Added

| File | Purpose |
|------|---------|
| `src/chetnaos/discourse/__init__.py` | Package exports |
| `src/chetnaos/discourse/intent_classifier.py` | Rule-based intent detection (11 intents) |
| `src/chetnaos/discourse/conversation_patterns.py` | Response schemas per intent |
| `src/chetnaos/discourse/response_planner.py` | Maps raw LLM text → section plan |
| `src/chetnaos/discourse/tone_engine.py` | Warm Hinglish tone; strips forbidden/telemetry language |
| `src/chetnaos/discourse/answer_composer.py` | Orchestrates pipeline + adaptive length |
| `tests/test_discourse_layer.py` | 13 unit/integration tests |

---

## Integration Point

**File modified:** `src/chetnaos/cycle/cognitive_cycle.py` (lines ~711–716)

```python
# Before
composed_reply = ResponseComposer.compose(final_output)

# After
discourse_reply = DiscourseLayer.transform(user_input, final_output)
composed_reply = ResponseComposer.compose(discourse_reply)
```

### Pipeline

```
Reasoning (ACT stage)
    ↓
Decision → Embodiment → final_output
    ↓
Telemetry narration guard (unchanged)
    ↓
DiscourseLayer.transform()     ← NEW
    ├─ IntentClassifier
    ├─ ResponsePlanner
    ├─ ToneEngine
    └─ AnswerComposer
    ↓
ResponseComposer.compose()     (unchanged)
    ↓
reply / composed_reply         (user-facing)
```

---

## Intent Classification (rule-based)

| Intent | Example triggers |
|--------|------------------|
| identity | who are you, tum kaun, introduce yourself |
| debug | why disabled, error, bug, embeddings, fix |
| learning | what is, explain, how does, samjhao |
| decision | should I, choose between, recommend |
| comparison | vs, compare, difference between |
| coding | code, function, python, implement |
| brainstorm | ideas for, alternatives, what if |
| emotional | samjha nahi, confused, frustrated |
| philosophical | consciousness, ethics, meaning |
| planning | plan, roadmap, next steps |
| casual | hi, thanks, short chat |

---

## Examples Before / After

### Who are you?

**Before (ResponseComposer only):**
> I am ChetnaOS — a Developmental Cognitive Organism designed to learn.

**After (Discourse + ResponseComposer):**
> Main Chetna hoon.
>
> Ek AI system jo memory, reasoning aur goals ki madad se kaam karta hai.
>
> Agar tum kisi topic par baat karna chaho, batao.

---

### Samjha nahi

**Before:**
> The previous answer covered embeddings, vector search, and sqlite storage in detail.

**After:**
> Koi baat nahi.
>
> Main thoda aur simple tareeke se samjhata hoon.

---

### Why are embeddings disabled?

**Before:** Flat paragraph dump.

**After (structured debug schema):**
> Dekhte hain — step by step.
>
> Observation  
> Embeddings are currently disabled.
>
> Possible cause  
> LIGHT_MODE defaults to true.
>
> Fix  
> Set EMBEDDINGS_ENABLED=true.
>
> Verification  
> Check /health.

(No cycle IDs, organ names, or confidence percentages exposed.)

---

## Test Results

```
tests/test_discourse_layer.py     13 passed
Full suite                        128 passed
```

Covers: intent rules, tone cleanup, identity/emotional canonical replies, debug structure, planner section mapping, discourse → ResponseComposer chain.

---

## Architecture Unchanged Confirmation

| Component | Status |
|-----------|--------|
| HTTP API routes | Unchanged |
| Request/response JSON shape | Unchanged |
| Cognitive cycle stages (27) | Unchanged |
| Memory store / recall | Unchanged |
| PromptBuilder / Reasoning | Unchanged |
| Frontend | Unchanged |
| ResponseComposer | Unchanged (still final sanitize pass) |

The discourse layer is **additive and modular** — it can be bypassed by removing the two-line hook without affecting any other subsystem.

---

## Tone Rules Applied

- Warm, calm, clear, respectful Hinglish openers where appropriate (`Achha sawal hai`, `Koi baat nahi`, `Dekhte hain`)
- Blocks: organism, entity, jeev, janwar, developmental cognitive organism
- Strips: cycle IDs, confidence %, organ telemetry
- No fake emotions, no childish tone, max one emoji
