# ChetnaOS Developmental Architecture Audit

**Date:** 2026-06-20  
**Scope:** Pre–GitHub push inspection only — no code modified  
**Method:** Static code trace, memory file inspection, `dashboard_snapshot()` verification, pytest run, historical experience log review

---

## Executive Summary

| Verdict | **Developmental organism prototype** |
|---------|--------------------------------------|

ChetnaOS has moved beyond a plain chatbot: developmental organs **exist**, **persist across restarts**, and **participate in the cognitive cycle**. Several organs are **write-heavy but read-light** — they update state and appear on the dashboard but are **not fully injected into the reasoning prompt**, so the LLM can still answer from generic knowledge instead of organism memory.

**Critical finding:** `Sleep.consolidate()` Phase 5 references undefined `domain_counts` — the next sleep cycle will raise `NameError` and abort consolidation.

**Tests:** 104 collected, **104 passed**, 2 deprecation warnings.

---

## 1. Identity Organ

**Status: PASS — ACTIVE**

| Check | Result |
|-------|--------|
| `memory/identity.json` exists | ✅ |
| Loaded at runtime | ✅ `Identity._load()` via `load_identity()` |
| Name, role, mission, values available | ✅ |
| Participates in reasoning context | ✅ `[IDENTITY]` block in `PromptBuilder.format_cognitive_context()` |

**Evidence**

- Live file: name `Chetna`, role `Developmental Cognitive Organism`, mission `Learn, reflect and help the founder build AGI`, `identity_stability: 0.95`, `development_stage: Early Organism`.
- `CognitiveCycle._build_reasoning_context()` passes identity fields into context.
- Each cycle: `identity.update(reflect_r, beliefs_r)` + `identity.tick()` at `UPDATE_IDENTITY` stage.

**Gaps (WARNING)**

- Prompt includes name/role/mission/stage but **not** `values`, `constitution`, or `beliefs_summary`.
- Older `experiences.jsonl` entries still say **"ChetnaOS"** — historical replies, not current identity file.

---

## 2. Relationship Organ

**Status: PASS — ACTIVE** (with historical leakage WARNING)

| Check | Result |
|-------|--------|
| `memory/relationships.json` exists | ✅ |
| Founder Mangla Prasad Pandey persistent | ✅ |
| Creator relationship protected | ✅ `FOUNDER_DEFAULT` merge on every load/update |
| Enters prompts | ✅ `[FOUNDER RELATIONSHIP]` block |

**Evidence**

```json
"founder": {
  "name": "Mangla Prasad Pandey",
  "role": "Founder",
  "relationship": "Creator",
  "attachment": "primary",
  "trust": "high",
  "importance": "maximum",
  "history_depth": "lifelong"
}
```

- `Relationship._load()` re-merges founder defaults — name/role/relationship cannot be overwritten by partial data.
- Post-cycle: `relationship.update("user", quality=...)` increments founder interactions/strength.
- Sleep path: `relationship_module.strengthen_after_sleep()` (when sleep completes).

**"Who am I?" test (historical)**

| Source | Behavior |
|--------|----------|
| Current prompt path | Would receive founder block — model *should* answer as Chetna addressing the founder |
| Historical log (`experiences.jsonl`) | ⚠️ **Leakage:** 2026-06-15 response to "I am mangla Founder" included *"the mangla that surrounds us"* — founder name treated as geography, not relationship memory |
| Historical log | 2026-06-15 "who I am?" answered about **Mangla Prasad Pandey** (correct entity, but answered *about* founder rather than *as* Chetna) |

**Note:** `FounderContext` (separate module, `founder_context.json` / defaults) also injects mission/milestones via `founder_ctx.get_system_context()` — parallel to Relationship organ.

---

## 3. Episodic Organ

**Status: WARNING — PARTIALLY ACTIVE**

| Check | Result |
|-------|--------|
| `memory/experiences.jsonl` exists | ✅ (large file, multi-day history) |
| Organ reads experiences | ✅ `EpisodicOrgan._load_all()` |
| "What happened yesterday?" grounded in memory | ⚠️ **Weak** |
| "What changed since yesterday?" grounded in memory | ⚠️ **Partial** |

**Evidence**

- Instantiated: `EpisodicOrgan(self.experience)` in `CognitiveCycle.__init__`.
- Dashboard: `episodic` snapshot with yesterday/today counts and highlights.
- Reasoning context: `[EPISODIC MEMORY]` block — **domain labels only** (e.g. `Yesterday: general; general`), **not** input/output text or achievements.

**Gap**

- `EpisodicOrgan.what_changed_since_yesterday()` exists but is **not** passed to the reasoning prompt.
- Temporal organ handles "what changed" with summary strings, not full episodic recall.
- LLM can hallucinate yesterday's events when episodic block is thin.

---

## 4. Temporal Continuity Organ

**Status: PASS — ACTIVE** (empty-yesterday WARNING)

| Check | Result |
|-------|--------|
| `memory/temporal_continuity.json` exists | ✅ |
| Yesterday / today / tomorrow connected | ✅ structure present |
| Enters prompts | ✅ `[TEMPORAL CONTINUITY]` block |
| Post-cycle updates | ✅ `temporal_continuity.tick()` after reflect |

**Live state**

```json
{
  "yesterday_summary": "",
  "today_summary": "general: workspace restore probe",
  "tomorrow_intentions": ["Answer about general: workspace restore probe", ...],
  "recent_changes": ["2026-06-19 — fair response in general", ...],
  "days_active": 0
}
```

**"What is today's focus?" / "What comes next?"**

- Today focus: derivable from `today_summary` + workspace `current_goal` (also in developmental dashboard block).
- Tomorrow: `tomorrow_intentions` populated from workspace goals — **functional but generic** ("Answer about general: …").
- `yesterday_summary` empty until day rollover — "what changed since yesterday" falls back to today-only narrative.

---

## 5. Development Organ

**Status: PASS — ACTIVE**

| Check | Result |
|-------|--------|
| `memory/development.json` exists | ✅ |
| Traits persist | ✅ curiosity, consistency, reflection, creativity, discipline, wisdom, research_maturity |
| Traits evolve over cycles | ✅ `_evolve_traits()` with small deltas (+0.003 good, -0.002 poor) |
| Dashboard exposure | ✅ `developmental` block + full `development` key preserved |

**Live traits (sample)**

| Trait | Value |
|-------|-------|
| curiosity | 0.502 |
| consistency | 0.5048 |
| reflection | 0.506 |
| research_maturity | 0.406 |

- `developmental_age` computed via `DevelopmentalAge.compute()` from quality ratio + trait average + identity stability — **not cycle-count alone**. ✅
- Post-cycle: `development.record()` + `apply_age()`.

**Gap:** Development traits **not injected into reasoning prompt** — influence is indirect via self-confidence calculation.

---

## 6. Reflection Organ

**Status: WARNING — PARTIALLY ACTIVE**

| Check | Result |
|-------|--------|
| `memory/reflections.json` exists | ✅ |
| Natural-language reflections accumulate | ✅ |
| Post-cycle recording | ✅ `reflection_organ.from_cycle()` |
| Sleep recording | ✅ when dream insights exist |
| Enters reasoning prompt | ❌ **No** |

**Live sample**

```json
{"text": "I have repeatedly focused on general.", "source": "cycle_reflection", "domain": "general"}
```

**"What have you learned recently?" / "What themes repeat?"**

- Data exists in `reflections.json` and `development.recurring_themes`.
- **Not passed to LLM** — answers likely generic unless model infers from other blocks.

---

## 7. Value Organ

**Status: WARNING — PARTIALLY ACTIVE**

| Check | Result |
|-------|--------|
| `memory/value_organ.json` exists | ✅ |
| Six values present | ✅ truth, growth, compassion, curiosity, alignment, service |
| Post-cycle influence | ✅ `value_organ.influence(quality)` adjusts weights |
| Enters reasoning prompt | ❌ **No** |

**Live weights:** truth 0.95, growth 0.902 (growth incremented after good cycles), alignment 0.92, etc.

Values **persist and drift slowly** but do **not** appear as a `[VALUES]` prompt block — LLM is not explicitly instructed to weigh decisions by value priorities.

---

## 8. Self Model Organ

**Status: WARNING — PARTIALLY ACTIVE**

| Check | Result |
|-------|--------|
| `memory/self_model.json` exists | ✅ |
| who_am_i / becoming / current_focus persisted | ✅ |
| Post-cycle updates | ✅ `record_change()`, `update(current_focus=...)` |
| Enters reasoning prompt | ⚠️ **Partial** |

**Persisted**

```json
{
  "who_am_i": "Chetna — a developmental cognitive organism learning with the founder.",
  "becoming": "A reflective partner in building AGI.",
  "current_focus": "Answer about general: workspace restore probe"
}
```

**Prompt block** (`[SELF MODEL]`) only includes:

- `self_confidence`
- `known_limits`

**Missing from prompt:** `who_am_i`, `becoming`, `matters_most`, `current_focus`, `recent_changes`.

**"Who are you becoming?" / "What is your current focus?"**

- Dashboard and JSON have answers.
- LLM prompt **may not** use them unless inferred from identity block or founder context.

---

## 9. Sleep Organ

**Status: FAIL — PARTIALLY ACTIVE (runtime bug)**

| Check | Result |
|-------|--------|
| Consolidation trigger | ✅ every 20 cycles (`SleepManager.sleep_every=20`) |
| Belief forget/strengthen | ✅ Phases 1–2 |
| Dream replay | ✅ Phase 3 (`_dream_replay`) |
| Themes / relationship / identity / reflections | ⚠️ Phase 5 **broken** |
| Last sleep logged | ✅ `memory/sleep_log.jsonl` |

**Last sleep entry**

```json
{
  "timestamp": "2026-06-16T11:17:15.672971",
  "cycle": 500,
  "action": "sleep_consolidation",
  "dream_insights": [{"insight": "Repeated exposure to 'general' domain — likely a core interest area."}]
}
```

**Critical bug (static analysis)**

In `src/chetnaos/organism/sleep.py` line 83:

```python
themes = list(domain_counts.keys()) if domain_counts else []
```

`domain_counts` is **never defined** in `consolidate()` — it only exists inside `_dream_replay()`. **Next sleep will raise `NameError`** before logging completes. Phases 1–4 may run but consolidation aborts; Phase 5 themes, relationship strengthen, identity `after_sleep`, and reflection recording may not execute.

**Status since bug:** No sleep log entries after 2026-06-16 — consistent with either low cycle volume or untested post-upgrade sleep path.

---

## 10. Dashboard Snapshot

**Status: PASS**

**New fields present (additive, backward compatible)**

| Field | Present |
|-------|---------|
| `developmental` | ✅ |
| `relationships` | ✅ |
| `episodic` | ✅ |
| `temporal_continuity` | ✅ |
| `reflections` | ✅ |
| `values` | ✅ |

**Legacy fields preserved:** `identity`, `skills`, `workspace`, `memory`, `beliefs`, `contradictions`, `development`, `sleep`, `health`, `cognitive_organs`, etc.

**`developmental` block keys verified:** curiosity, consistency, reflection, creativity, discipline, wisdom, research_maturity, identity_stability, relationship_strength, development_stage, developmental_age, current_focus, recurring_themes, recent_lessons, development_timeline, self_model, what_changed.

**API:** `GET /api/dashboard` → `rt._cycle.dashboard_snapshot()` — unchanged route, extended payload.

---

## 11. Runtime Integration — One Conversation Trace

**Order of organ participation in `CognitiveCycle.run()`**

| Phase | Organs involved |
|-------|-----------------|
| Pre-ACT context build | SelfModel (update), GoalManager, Curiosity, Emotion, **Identity**, **Founder Relationship**, **Temporal**, **Episodic** → reasoning prompt |
| ACT (LLM) | Reasoning + founder_context string + cognitive_context |
| EXPERIENCE | Experience → `experiences.jsonl` |
| REFLECT / META | Reflection (cycle quality), MetaCognition |
| UPDATE_IDENTITY | **Identity** update + tick |
| SLEEP (every 20) | **Sleep** → beliefs, dreams, **Relationship**, **Identity**, **Development**, **ReflectionOrgan** |
| Post-cycle side effects | Experience.enrich_last, **Development**, **Relationship**, **ValueOrgan**, **TemporalContinuity**, **ReflectionOrgan**, **SelfModel** |

**Evidence chain (inspectable without LLM call)**

```
_build_reasoning_context() keys:
  active_goal, beliefs, self_model, curiosity, emotion,
  temporal, episodic, identity, founder_relationship

NOT in context:
  values, reflections, development traits, full self_model narrative
```

**Response path:** `ResponseComposer.compose(final_output)` → sanitized `reply` (strips cycle counts, confidence %, organ telemetry).

---

## 12. Generic LLM Leakage

**Status: WARNING**

| Question | Risk | Evidence |
|----------|------|----------|
| "What changed since yesterday?" | **High** | Temporal block often has empty yesterday; episodic block is domain-only; model may invent narrative |
| "Who am I?" | **Medium** | Identity + founder blocks present; historical log shows conflation of "mangla" with geography |
| "What are you becoming?" | **High** | `becoming` field not in prompt — likely generic AGI/partner language |
| "What have you learned recently?" | **High** | Reflections not in prompt |
| "What themes repeat?" | **Medium** | Themes in development JSON + dashboard; not in prompt |

**Mitigations in place**

- Founder relationship block reduces "random person" answers.
- ResponseComposer hides internal telemetry (does not fix memory grounding).
- Belief confidence block anchors high-confidence beliefs.

**Residual risk:** LLM is still primary author; thin memory injection → **plausible but ungrounded** answers remain possible.

---

## 13. Dead / Partial Organs

| Organ (spec) | Implementation | Runtime read | Runtime write | Classification |
|--------------|----------------|--------------|---------------|----------------|
| Identity | `organism/identity.py` | Prompt + dashboard | Every cycle | **ACTIVE** |
| Relationship | `organism/relationship.py` | Prompt + dashboard | Every cycle + sleep | **ACTIVE** |
| Episodic | `organism/episodic_organ.py` | Prompt (thin) + dashboard | Via Experience | **PARTIALLY ACTIVE** |
| Temporal | `organism/temporal_continuity.py` | Prompt + dashboard | Every cycle | **ACTIVE** |
| Development | `organism/development.py` | Dashboard only | Every cycle | **PARTIALLY ACTIVE** |
| Reflection (organ) | `organism/reflection_organ.py` | Dashboard only | Every cycle + sleep | **PARTIALLY ACTIVE** |
| Value | `organism/value_organ.py` | Dashboard only | Post-cycle influence | **PARTIALLY ACTIVE** |
| Self Model | `cognition/self_model.py` | Prompt (partial) + dashboard | Every cycle | **PARTIALLY ACTIVE** |
| Sleep | `organism/sleep.py` | Dashboard | Every 20 cycles | **PARTIALLY ACTIVE** (bug) |
| Difference | — | — | — | **NOT IMPLEMENTED** (contradictions cover related ground) |
| Concern | — | — | — | **NOT IMPLEMENTED** |
| Equilibrium | `homeostasis.py` | Dashboard `health` | Post-cycle check | **PARTIALLY ACTIVE** |
| Attention / Memory / Prediction | attention, memory, simulation | Full cycle | Full cycle | **ACTIVE** (legacy architecture) |

**Files never read at runtime (developmental set):** None of the six new JSON files are dead — all are loaded. **EpisodicOrgan** is the weakest reader (minimal prompt content).

---

## 14. Organ Health Table

| Organ | Status | Notes |
|-------|--------|-------|
| Identity | **PASS** | Persisted, loaded, prompt + cycle |
| Relationship | **PASS** | Founder locked; historical leakage in old chats |
| Episodic | **WARNING** | Persisted; prompt lacks event detail |
| Temporal | **PASS** | Active; yesterday often empty same-day |
| Development | **PASS** | Traits evolve; not in prompt |
| Reflection | **WARNING** | Accumulates; not in prompt |
| Values | **WARNING** | Weights drift; not in prompt |
| Self Model | **WARNING** | Full narrative not in prompt |
| Sleep | **FAIL** | `domain_counts` NameError on Phase 5 |

---

## 15. Test Coverage

| Metric | Value |
|--------|-------|
| Test files | 17 |
| Tests collected | **104** |
| Pass | **104** |
| Fail | 0 |

**Developmental tests (`tests/test_developmental_organs.py`) — 8 tests**

- Identity defaults
- Founder relationship preservation
- Development trait evolution
- Developmental age from quality
- ResponseComposer sanitization
- Temporal continuity tick
- Reflection organ recording
- Value organ priorities

**Missing tests (recommended before treating as production organism)**

| Area | Gap |
|------|-----|
| Dashboard `developmental` block | No assertion on new keys |
| Prompt injection | No test that identity/founder/temporal blocks appear in system prompt |
| Episodic grounding | No test for yesterday recall content |
| Sleep Phase 5 | No integration test; bug undetected |
| End-to-end leakage | No test that "what changed" cites temporal/episodic data |
| Self model narrative | No test that becoming/focus reach prompt |
| Value organ → reasoning | No test (currently N/A — not wired) |

---

## Final Classification

### Is ChetnaOS currently…?

| Level | Fit | Evidence |
|-------|-----|----------|
| Advanced chatbot | ✅ Exceeded | 27-stage cycle, persistent memory, belief system |
| Cognitive architecture | ✅ Yes | Working memory, goals, beliefs, meta-cognition, executive controller |
| **Developmental organism prototype** | ✅ **Best fit** | Organs persist, cycle writes state, dashboard exposes growth; prompt integration incomplete |
| Developmental organism | ⚠️ Not yet | Several organs write-only for LLM; sleep bug; leakage in temporal/self questions |
| Self-developing organism | ❌ Not yet | No closed loop where development reliably reshapes behavior; age/stage mostly observational |

### Recommended pre-push checklist (report only — no changes made)

1. **Fix sleep `domain_counts` bug** before next production sleep cycle.
2. **Enrich reasoning prompt** with reflections, values, self_model narrative, episodic highlights (input snippets).
3. **Add integration tests** for dashboard developmental keys and prompt blocks.
4. **Run one live sleep cycle** in staging after fix to verify Phase 5.
5. **Optional:** Migrate historical identity naming (ChetnaOS → Chetna) in reply templates via system prompt emphasis.

---

*Audit performed without code modification. One runtime trace of `dashboard_snapshot()` and `_build_reasoning_context()` was executed to verify live integration.*
