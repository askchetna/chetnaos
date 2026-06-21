# Discourse Layer v2 Report

**Date:** 2026-06-21  
**Focus:** Discourse Intelligence + Style Intelligence + Context Awareness

---

## What Changed (v1 → v2)

| Area | v1 | v2 |
|------|----|----|
| Schemas | Partial / mixed keys | Full v2 schemas (Introduction, Importance, Cause, Clarify, etc.) |
| Style | `tone_engine.py` only | **`language_style_engine.py`** — natural Hinglish, anti-robotic |
| Verbosity | Basic short/structured | **`verbosity_control.py`** — short / medium / structured / code_first |
| Context | None | **`context_awareness.py`** — follow-up, correction, confusion, agreement |
| Quality | Implicit | **`quality_goals.py`** — clarity, correctness, helpfulness, naturalness, brevity, trustworthiness |
| Memory | None | Dedupe vs prior assistant turns; skip repeated identity |

---

## Files Added (v2)

| File | Role |
|------|------|
| `language_style_engine.py` | Natural Hinglish; forbidden terms; light openers |
| `context_awareness.py` | Dialogue acts + history dedupe + identity repetition guard |
| `verbosity_control.py` | Adaptive length per intent/complexity |
| `quality_goals.py` | Response quality polish pass |

## Files Updated

| File | Change |
|------|--------|
| `conversation_patterns.py` | v2 section schemas |
| `response_planner.py` | v2 aliases; coding code-first extraction |
| `answer_composer.py` | Full v2 pipeline orchestration |
| `tone_engine.py` | Delegates to LanguageStyleEngine |
| `__init__.py` | Exports `QUALITY_GOALS` |
| `cognitive_cycle.py` | Passes `conversation_context` to discourse (internal only) |
| `tests/test_discourse_layer.py` | 17 tests including context/verbosity/coding |

---

## Integration (unchanged architecture)

```python
discourse_reply = DiscourseLayer.transform(
    user_input, final_output, conversation_context=conversation_context,
)
composed_reply = ResponseComposer.compose(discourse_reply)
```

APIs, memory, cognitive cycle stages: **unchanged**.

---

## v2 Response Schemas

**Identity:** Introduction → Purpose → Capabilities → Invitation  
**Learning:** Definition → Intuition → Example → Importance → Summary  
**Debug:** Observation → Cause → Fix → Verification  
**Decision:** Goal → Options → Tradeoffs → Recommendation → Reason  
**Planning:** Goal → Priorities → Steps → Risks → Next action  
**Comparison:** Criteria → Differences → Pros → Cons → Recommendation  
**Emotional:** Acknowledge → Clarify → Perspective → Practical help  

---

## Context Awareness

| Dialogue act | Trigger examples | Behavior |
|--------------|------------------|----------|
| follow_up | tell me more, phir, aur | Shorter; no identity re-intro |
| correction | galat, actually, wrong | Prefix acknowledgment |
| confusion | samjha nahi, confused | Clarify template |
| agreement | thanks, theek, got it | Brief reply |

---

## Examples

### Who are you? (first time)
> Main Chetna hoon.  
> Ek AI system jo memory, reasoning aur goals ki madad se kaam karta hai.  
> Agar tum kisi topic par baat karna chaho, batao.

### Who are you? (repeat in same thread)
> Main Chetna hoon — ek cognitive AI system.

### Follow-up after identity (embeddings question)
Identity lines stripped from answer; content-only response.

### Samjha nahi
> Koi baat nahi.  
> Main thoda aur simple tareeke se samjhata hoon.

### Coding
Code block placed **first**, then context/caveats.

---

## Test Results

```
tests/test_discourse_layer.py   17 passed
Full suite                      132 passed
```

---

## Architecture Confirmation

| Component | Status |
|-----------|--------|
| HTTP APIs | Unchanged |
| Memory subsystem | Unchanged |
| Cognitive cycle (27 stages) | Unchanged (+ optional context arg to discourse hook) |
| Frontend | Unchanged |
| ResponseComposer | Unchanged (final sanitize) |
