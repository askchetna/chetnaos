# Identity Contamination Fix Report

**Date:** 2026-06-21  
**Issue:** Chetna described itself as an animal/biological organism (e.g. Hindi: *"Main ek vikasit gyanik janwar hoon"*, *"Main ek jeev hoon"*).

---

## Root Cause

Contamination entered the LLM through **multiple layers**, not a single bug:

| Source | Contamination |
|--------|----------------|
| `identity.py` DEFAULT + `memory/identity.json` | `role: "Developmental Cognitive Organism"`, `description: "...cognitive organism."` |
| `self_model.py` + `memory/self_model.json` | `who_am_i: "Chetna — a developmental cognitive organism..."` |
| `prompt_builder.py` BASE_TEMPLATE | `"You are ChetnaOS — a Developmental Cognitive Organism."` |
| `constitution/mission.py` | `"recursively self-developing cognitive organism"` |
| `frontend/index.html` | `"A Living Intelligence"` (6 places) |
| `frontend/dashboard.html` | `"Developmental cognitive organism"`, `"Computational Developmental Organism"` |
| Long-term memory recall | Could re-inject past self-descriptions containing *organism* |

The LLM translated English *organism* framing into Hindi *janwar* / *jeev* when answering identity questions.

No contaminated rows were found in repo-tracked `experiences.jsonl`. Runtime `mem.db` is gitignored; recall-time filtering now ignores contaminated rows if present.

---

## Search Results (repo-wide)

Terms searched: `janwar`, `organism`, `creature`, `living intelligence`, `biological`, `gyanik`, `jeev`, `alive`, `lifeform`.

**User-facing / prompt injection (fixed):**

- `src/chetnaos/organism/identity.py`
- `src/chetnaos/cognition/self_model.py`
- `src/chetnaos/reasoning/prompt_builder.py`
- `src/chetnaos/constitution/mission.py`
- `src/chetnaos/reasoning/honesty_guard.py`
- `memory/identity.json`, `memory/self_model.json`
- `frontend/index.html`, `frontend/dashboard.html`

**Internal module names (`src/chetnaos/organism/` package):** unchanged — architecture preserved.

**Reports / JSON artifacts:** historical references only; not loaded at runtime.

---

## Files Changed

| File | Why |
|------|-----|
| `src/chetnaos/memory/identity_guard.py` | **NEW** — contamination detection, memory filter, identity scrubbing, post-response guard, optional DB purge helper |
| `src/chetnaos/organism/identity.py` | Canonical identity: Cognitive AI System; `biological/animal/living_organism: false`; scrub on load |
| `memory/identity.json` | Persisted identity aligned with new canonical fields |
| `src/chetnaos/cognition/self_model.py` | Canonical `who_am_i`; scrub on load |
| `memory/self_model.json` | Persisted self-model aligned |
| `src/chetnaos/memory/schemas.py` | Pydantic defaults + `type`, `biological`, `animal`, `living_organism` fields |
| `src/chetnaos/reasoning/prompt_builder.py` | Base prompt, `[IDENTITY]` block, `[IDENTITY CONSTRAINTS]`, memory grounding, contaminated recall filter |
| `src/chetnaos/reasoning/honesty_guard.py` | System + post-response guard for animal/organism/jeev/janwar claims |
| `src/chetnaos/constitution/mission.py` | Removed *cognitive organism* from constitution mission text |
| `src/chetnaos/memory/store.py` | Filter contaminated rows from `search()` and `recent()` at read time |
| `src/chetnaos/cycle/cognitive_cycle.py` | Dashboard role label: Research Organism → Research Partner |
| `frontend/index.html` | All `"A Living Intelligence"` → `"Cognitive AI System"` |
| `frontend/dashboard.html` | Organism UI labels → Cognitive AI System framing |
| `tests/test_identity_guard.py` | **NEW** — guard, scrub, and prompt constraint tests |
| `tests/test_developmental_organs.py` | Updated identity assertions |
| `tests/test_memory_store.py` | Test data no longer uses word *organism* (would be filtered) |

---

## New Identity (canonical)

```
Name: Chetna
Type: Cognitive AI System
Biological: false
Animal: false
Living organism: false
Purpose: Serve with truth and compassion.
```

Self-model canonical line:

> I am Chetna, a cognitive AI system with memory, goals, and reasoning.

---

## Prompt Constraints Added

Hard blocks in system prompt (`[IDENTITY CONSTRAINTS]` + `[HONESTY GUARD]`):

- Never describe yourself as: animal, organism, creature, lifeform, biological being, living intelligence, **jeev**, **janwar**
- Required framing: *"I am Chetna, a cognitive AI system. I am not biological and not an animal."*

Post-response `apply_identity_guard()` rewrites contaminated self-claims before the user sees them.

---

## Memory Handling

- **Recall filter:** `MemoryStore.search()` / `recent()` skip rows matching contamination patterns
- **Prompt filter:** `PromptBuilder.with_memory()` skips contaminated recalled items
- **Purge helper:** `purge_contaminated_memories(db)` available for one-time DB cleanup (not auto-run — avoids destructive surprise)

---

## Verification

```text
115 passed (full test suite)
```

Prompt now opens with:

> You are Chetna, a cognitive AI system with memory, goals, and reasoning. You are not biological, not an animal, and not a living organism.

Guard rewrite:

| Input | Output |
|-------|--------|
| `Main ek vikasit gyanik janwar hoon` | `I am Chetna, a cognitive AI system. I am not biological and not an animal.` |
| `Main ek jeev hoon` | `I am Chetna, a cognitive AI system. I am not biological and not an animal.` |

**Expected live answers:**

- *who are you?* → cognitive AI system identity; not biological; not an animal
- *tum janwar ho?* → denial + correct identity framing

---

## Not Changed (by design)

- API routes and response shapes
- `src/chetnaos/organism/` package structure (internal module naming)
- `Existence.pulse()` still returns `alive: true` in cycle telemetry (not injected into user-facing prompts)
- Developmental age internal stage enum strings in `developmental_age.py` (dashboard uses scrubbed identity stage names)
