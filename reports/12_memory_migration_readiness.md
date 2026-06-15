# 12 — Memory Migration Readiness Report

**Date:** 2026-06-15  
**Phase:** 2 complete (facade layer, no data migration)

---

## Current Stores

| Store | Location | Type | Live Writer | Unified Facade |
|-------|----------|------|-------------|----------------|
| Vector memory | `mem.db` → `memories` table | SQLite | `memory/db.py`, `organism/memory.py` | **MemoryStore** |
| Episodic | `memory/experiences.jsonl` | JSONL | `organism/experience.py` | `EpisodicMemory` |
| Semantic (beliefs) | `memory/beliefs.json` | JSON | `organism/beliefs.py` | `SemanticMemory` |
| Semantic (lessons) | `memory/lessons.jsonl` | JSONL | `organism/learning.py` | `SemanticMemory` |
| Procedural (skills) | `memory/skills.json` | JSON | `organism/skills.py` | `ProceduralMemory` |
| Procedural (habits) | `memory/habits.json` | JSON | `organism/habit.py` | `ProceduralMemory` |
| Working | in-process + `mem_hierarchy.json` | RAM + JSON | `organism/memory_hierarchy.py` | `WorkingMemory` |
| Identity | `memory/identity.json` | JSON | `organism/identity.py` | validated, not facaded |
| Purpose | `memory/purpose.json` | JSON | `organism/purpose.py` | validated, not facaded |
| Workspace | `memory/workspace_state.json` | JSON | `organism/workspace_state.py` | validated, not facaded |
| Development | `memory/development.json` | JSON | `organism/development.py` | not facaded |
| Relationships | `memory/relationships.json` | JSON | `organism/relationship.py` | not facaded |
| Training goals | `memory/training_goals.json` | JSON | `organism/self_trainer.py` | not facaded |
| Contradictions | `memory/contradictions.json` | JSON | `organism/contradiction_tracker.py` | not facaded |
| Archived Smriti | `mem.db` → `smriti` table (if exists) | SQLite | **archived v0.9 only** | not migrated |

---

## Duplicate Schemas

| Issue | Evidence | Risk |
|-------|----------|------|
| `mem.db` may contain `smriti` table from archived `Smriti` | `archive/v0.9_legacy/backend/memory.py` | Low if table empty |
| Beliefs in JSON + vector store | beliefs.json + mem.db embeddings | Medium — same facts, different indexes |
| Episodic in JSONL + vector interactions | experiences.jsonl + memory.store() | Medium — dual write, no merge |
| Working memory split | RAM (`_working`) vs `mem_hierarchy.json` | Low — by design |

---

## Unsafe Migrations (do NOT do yet)

| Migration | Why unsafe |
|-----------|------------|
| Merge JSON files into SQLite | Would break organism module paths |
| Rename `memory/` folder | Hardcoded paths in 15+ organism modules |
| Delete `memory/db.py` | `backend/agent.py` imports `memory_db` directly |
| Consolidate beliefs into vector-only | Loses structured confidence/source fields |
| Auto-fix corrupt JSON in place | Violates "never destroy invalid data" rule |

---

## Recommended Merge Path (Phase 3+)

```
Phase 3a: Route all new vector writes through MemoryStore only (done for organism/memory.py)
Phase 3b: Add EpisodicMemory.recall_recent() reading experiences.jsonl
Phase 3c: Single read API on MemoryStore for dashboard
Phase 3d: Migrate Smriti rows → memories table (if any exist) with adapter script
Phase 3e: Package move src/chetnaos/memory → chetnaos/memory (with compat shims)
```

---

## Data Loss Risk Assessment

| Operation | Data loss risk |
|-----------|----------------|
| Phase 2 facade layer | **NONE** — no data moved |
| MemoryStore.delete() | **LOW** — explicit id only, logged |
| JSON validation with backup | **NONE** — source preserved on failure |
| Future Smriti merge | **MEDIUM** — requires dry-run + row count verification |
| Future folder rename | **HIGH** — must update all `../../..memory` paths first |

---

## Backward Compatibility Status

| Import path | Status |
|-------------|--------|
| `from memory.db import memory_db` | **WORKING** |
| `from src.chetnaos.organism.memory import Memory` | **WORKING** (delegates to MemoryStore) |
| `from src.chetnaos.memory.store import get_memory_store` | **NEW — WORKING** |
| Cognitive cycle `self.memory.store()` | **WORKING** |
| `/api/agent` memory search | **WORKING** (uses memory_db directly) |

---

## Phase 2 Exit Criteria

| Criterion | Status |
|-----------|--------|
| One MemoryStore abstraction | DONE |
| Facades wrap existing modules | DONE |
| No data migration | DONE |
| Compatibility layer | DONE |
| JSON schema audit | DONE (`reports/11_json_schema_audit.md`) |
| Pydantic validation (5 files) | DONE |
| Tests | DONE (`tests/test_memory_store.py`) |
| Phase 1 baseline preserved | Must pass `scripts/phase2_gate.py` |

---

## Next Phase

**Phase 3** (when approved): Extract executive controller + package restructure — **not started** per Phase 2 constraints.
