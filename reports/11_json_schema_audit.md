# 11 — JSON Persistence Schema Audit

**Date:** 2026-06-15  
**Method:** Read-only inspection of `memory/*.json` files  
**Action taken:** None — no files modified

---

## Summary

| File | Format | Valid JSON | Pydantic Model | Live Validation |
|------|--------|------------|----------------|-----------------|
| `identity.json` | object | YES | `IdentitySchema` | PASS |
| `beliefs.json` | array | YES | `BeliefsSchema` | PASS |
| `purpose.json` | object | YES | `PurposeSchema` | PASS |
| `skills.json` | object (map) | YES | `SkillsSchema` | PASS |
| `workspace_state.json` | object | YES | `WorkspaceSchema` | PASS |
| `habits.json` | object (map) | YES | **MISSING** | Not validated yet |
| `development.json` | object | YES | **MISSING** | Not validated yet |
| `relationships.json` | object | YES | **MISSING** | Not validated yet |
| `training_goals.json` | array | YES | **MISSING** | Not validated yet |
| `contradictions.json` | array | YES | **MISSING** | Not validated yet |
| `mem_hierarchy.json` | object | YES | **MISSING** | Not validated yet |

---

## Per-File Schema (evidence from repository)

### `identity.json`

```json
{
  "name": "string",
  "version": "string",
  "level": "string",
  "description": "string",
  "core_traits": ["string"],
  "cycle_count": "integer",
  "updates": "integer",
  "last_growth": "ISO datetime string (optional)",
  "last_active": "ISO datetime string (optional)"
}
```

**Observed:** 28 cycles, 19 updates. Matches `Identity.DEFAULT` in `organism/identity.py`.

---

### `beliefs.json`

Array of:

```json
{
  "id": "integer",
  "text": "string",
  "confidence": "float 0-1 (observed up to 1.0)",
  "source": "constitution | learning | experience",
  "created": "ISO datetime (optional)"
}
```

**Observed:** 4 beliefs (3 constitution + 1 learning).

---

### `purpose.json`

```json
{
  "statement": "string",
  "refinements": "integer",
  "version": "integer",
  "last_refinement": "string (optional)"
}
```

**Observed:** 19 refinements, version 20.

---

### `skills.json`

Map of skill name → object:

```json
{
  "score": "float 0-1",
  "interactions": "integer",
  "category": "core | technical | social | applied",
  "last_practiced": "ISO datetime (optional)"
}
```

**Observed:** 8 skills. `Coding` and `Communication` have `last_practiced`.

---

### `habits.json`

Map of `"intent:domain"` → integer count:

```json
{
  "question:general": 14,
  "statement:general": 7
}
```

**Writer:** `organism/habit.py`  
**No schema validation model yet.**

---

### `development.json`

```json
{
  "total_cycles": "integer",
  "good_cycles": "integer",
  "poor_cycles": "integer",
  "avg_confidence": "float",
  "growth_events": "array"
}
```

**Observed:** 28 total, 19 good, 0 poor, avg_confidence 0.646.

---

### `relationships.json`

```json
{
  "user": {
    "interactions": "integer",
    "positive": "integer"
  }
}
```

**Writer:** `organism/relationship.py`

---

### `workspace_state.json`

```json
{
  "current_thought": "string",
  "current_goal": "string",
  "current_hypothesis": "string",
  "current_plan": "string",
  "active_priority": "integer 0-100",
  "pending_contradictions": "integer",
  "unsolved_questions": ["string"],
  "artifacts": [{"name": "string", "type": "string", "created_at": "ISO datetime"}],
  "last_updated": "ISO datetime (optional)"
}
```

**Observed:** 10 artifacts stored.

---

### `training_goals.json`

Array of:

```json
{
  "skill": "string",
  "current_pct": "float",
  "target_pct": "float",
  "gap_pct": "float",
  "priority": "float",
  "suggested_training": "string",
  "practice_topics": "string",
  "expected_improvement": "string",
  "category": "string"
}
```

**Writer:** `organism/self_trainer.py`  
**Observed:** 3 goals (Sales, Business, Coding).

---

## JSONL Files (not in Step 4 list but referenced)

| File | Line schema |
|------|-------------|
| `experiences.jsonl` | `{timestamp, input, output, confidence, domain, cycle}` |
| `lessons.jsonl` | `{lesson, quality}` |
| `artifacts.jsonl` | written by `artifacts.py` |
| `civilization.jsonl` | written by `civilization_memory.py` |
| `meta_cognition.jsonl` | written by `meta_cognition.py` |

---

## Risks

| Risk | Severity |
|------|----------|
| `confidence` / `score` can exceed 1.0 in raw writes | Low — schemas clamp on read |
| No validation on habits/development at load time | Medium — silent `except: pass` in organism modules |
| JSONL files have no line-level validation | Medium — corrupt line skipped silently |

---

## Phase 2 Validation Coverage

Models implemented in `src/chetnaos/memory/schemas.py` for: identity, beliefs, purpose, skills, workspace.

Backup on failure: `memory/.validation_backups/` (never overwrites source).
