# ChetnaOS — Memory Embeddings Root Cause Analysis & Fix

**Date:** 2026-06-17  
**Issue:** Dashboard shows `embeddings_enabled=false`, `db_with_embedding=0`, `without_embedding≈861`, vector recall returns 0 matches.

---

## Executive Summary

Embeddings are disabled by default because **`LIGHT_MODE` defaults to `true`**, which makes **`EMBEDDINGS_ENABLED` default to `false`** when that env var is unset. With embeddings off, every `upsert()` stores `embedding=NULL`, so all 917 `mem.db` rows have no vectors. Vector search cannot run; recall falls back to sparse keyword matching (or returns empty when keywords do not overlap).

Even after enabling embeddings via `EMBEDDINGS_ENABLED=true`, **`sentence-transformers` is not in `requirements.txt` and is not installed** in this environment, so the model never loads (`embedding_model_loaded=false`).

---

## Root Cause Analysis (Evidence from Code)

### A) Why embeddings are disabled

| Source | Evidence |
|--------|----------|
| `memory/embedding_config.py` | `LIGHT_MODE` defaults `True`; if `EMBEDDINGS_ENABLED` env absent → `embeddings_enabled = not light_mode` → **False** |
| `memory/db.py` `get_embedding_model()` | Returns `None` when `get_embeddings_enabled()` is False; prints sparse-only message |
| `memory/db.py` `get_embedding()` | Returns `None` when model is `None` |
| Live DB | `SELECT COUNT(*) … WHERE embedding IS NOT NULL` → **0 of 917** |

```python
# memory/embedding_config.py (resolve_embedding_settings)
light_mode = _parse_bool(os.getenv("LIGHT_MODE"), default=True)
embeddings_env = os.getenv("EMBEDDINGS_ENABLED")
if embeddings_env is not None:
    embeddings_enabled = _parse_bool(embeddings_env, default=not light_mode)
else:
    embeddings_enabled = not light_mode  # False when LIGHT_MODE=true
```

### B) Does LIGHT_MODE automatically force EMBEDDINGS_ENABLED=False?

**Yes, when `EMBEDDINGS_ENABLED` is not set in the environment.**

- `LIGHT_MODE=true` (default) + no `EMBEDDINGS_ENABLED` → `EMBEDDINGS_ENABLED=false`
- `LIGHT_MODE=false` + no `EMBEDDINGS_ENABLED` → `EMBEDDINGS_ENABLED=true`

LIGHT_MODE does **not** hard-force False when `EMBEDDINGS_ENABLED` is explicitly set (see C).

### C) Can Replit environment variables override it?

**Yes.** Replit Secrets / env vars are standard `os.environ` values read by `load_dotenv()` + `resolve_embedding_settings()`.

- `.replit` workflow runs: `uvicorn backend.app:app --host 0.0.0.0 --port 5000` (no embedding vars set in file)
- Set in Replit Secrets: `EMBEDDINGS_ENABLED=true` → embeddings enabled even with `LIGHT_MODE=true`
- Verified locally: `EMBEDDINGS_ENABLED=true` → `resolve_embedding_settings()` returns `(True, True)`

### D) Does the health endpoint report wrong values?

**No — it reports `backend.config.Settings`, which now shares the same resolver as `memory/db.py`.**

Prior risk: `memory/db.py` had duplicate module-level flags that could diverge from `Settings`. **Fixed** by centralizing in `memory/embedding_config.py`.

`GET /health` returns `settings.LIGHT_MODE` and `settings.EMBEDDINGS_ENABLED` from `backend/api/health.py`.

`GET /api/debug/embeddings` returns live memory-layer flags + DB counts + `embedding_model_loaded`.

### E) Does memory insertion currently store vectors?

**Only when embeddings are enabled AND the model loads successfully.**

```python
# memory/db.py upsert()
embedding = get_embedding(text)
# INSERT ... embedding.tobytes() if embedding is not None else None
```

With default config: `get_embedding()` → `None` → **BLOB column stays NULL**.

Path: `Memory.store()` → `MemoryStore.upsert()` → `MemoryDB.upsert()` → `get_embedding()`.

### F) Why existing memories have with_embedding=0, without_embedding>800?

1. System has run since inception with `EMBEDDINGS_ENABLED=false` (default under `LIGHT_MODE=true`).
2. All historical inserts stored text + meta but **no embedding vector**.
3. Count grew to **917 rows**, **0 with embeddings** (verified 2026-06-17).
4. `experiences.jsonl` episodic memories are a separate JSON store — not searched by `mem.db` vector/sparse search.

### G) Why "Retrieved = 0" in recall trace

When embeddings disabled and sparse keyword overlap fails:

```python
# memory/db.py search_with_trace failure_point
"embeddings_disabled_and_no_keyword_overlap"
```

Vector path in `_vector_search()` returns `[]` immediately if `get_embedding(query)` is `None`, or if no rows have embeddings.

---

## Startup Flow (Boot → Memory Init)

```
uvicorn backend.app:app
  └─ backend/app.py
       ├─ from backend.config import get_settings
       │    └─ load_dotenv() + resolve_embedding_settings()
       ├─ app.state.settings = settings
       └─ @startup: refresh_embedding_config() + reset_embedding_model()
            └─ get_runtime() [first HTTP request or startup]
                 └─ ChetnaRuntime → CognitiveCycle()
                      └─ organism/memory.py imports get_memory_store()
                           └─ MemoryStore → memory.db.memory_db (singleton)
                                └─ MemoryDB.__init__ → init_db()
```

**First embedding decision** happens at `memory/embedding_config.py` import time; **re-synced** on app startup.

---

## Fixes Implemented

### FIX 1 — Explicit `EMBEDDINGS_ENABLED` overrides `LIGHT_MODE`

**New file:** `memory/embedding_config.py` — single resolver used by both `backend/config.py` and `memory/db.py`.

**Updated:** `backend/app.py` calls `refresh_embedding_config()` on startup.

### FIX 2 — Backfill script

**New file:** `scripts/backfill_embeddings.py`

- Opens `mem.db`
- Updates rows `WHERE embedding IS NULL`
- Skips already-embedded rows (safe restart)
- Progress every 100 rows
- Requires `EMBEDDINGS_ENABLED=true` + `sentence-transformers` installed

### FIX 3 — Diagnostics endpoint

**New file:** `backend/api/debug_embeddings.py`  
**Route:** `GET /api/debug/embeddings`

```json
{
  "light_mode": true,
  "embeddings_enabled": false,
  "total_memories": 917,
  "with_embedding": 0,
  "without_embedding": 917,
  "embedding_model_loaded": false
}
```

### FIX 4 — Dashboard

**Updated:** `frontend/dashboard.html` — **Embedding Diagnostics** card (top of grid) showing:
- Light Mode
- Embeddings Enabled
- Embedding Model Status
- DB With / Without Embeddings

### FIX 5 — This report

---

## Files Changed

| File | Change |
|------|--------|
| `memory/embedding_config.py` | **NEW** — shared env resolution |
| `memory/db.py` | Use shared config; add `is_embedding_model_loaded()`, `reset_embedding_model()` |
| `backend/config.py` | Delegate to `resolve_embedding_settings()` |
| `backend/app.py` | Startup refresh + `app.state.settings` at boot |
| `backend/api/debug_embeddings.py` | **NEW** — diagnostics endpoint |
| `backend/api/__init__.py` | Register debug router |
| `scripts/backfill_embeddings.py` | **NEW** — vector backfill |
| `frontend/dashboard.html` | Embedding Diagnostics panel |
| `report.md` | This document |

---

## Exact Code Changes (Key Snippets)

### Shared resolver (`memory/embedding_config.py`)

```python
def resolve_embedding_settings() -> tuple[bool, bool]:
    light_mode = _parse_bool(os.getenv("LIGHT_MODE"), default=True)
    embeddings_env = os.getenv("EMBEDDINGS_ENABLED")
    if embeddings_env is not None:
        embeddings_enabled = _parse_bool(embeddings_env, default=not light_mode)
    else:
        embeddings_enabled = not light_mode
    return light_mode, embeddings_enabled
```

### Upsert still gates on model (`memory/db.py`)

```python
embedding = get_embedding(text)
# ... VALUES (?, ?, ?) with embedding.tobytes() if embedding is not None else None
```

---

## Migration Command

**Prerequisite:** Install embedding model dependency:

```powershell
pip install sentence-transformers
```

**Enable embeddings and backfill:**

```powershell
cd C:\Users\mangl\OneDrive\Desktop\ChetnaOS.v1
$env:EMBEDDINGS_ENABLED = "true"
python scripts/backfill_embeddings.py --db mem.db
```

**Replit:** Add Secret `EMBEDDINGS_ENABLED=true`, install `sentence-transformers` in Replit packages, then run backfill once.

**Restart server after env change:**

```powershell
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

---

## Verification Commands

```powershell
# 1. Config resolution
python -c "from memory.embedding_config import resolve_embedding_settings; print(resolve_embedding_settings())"
# Default: (True, False)
# With EMBEDDINGS_ENABLED=true: (True, True)

# 2. DB embedding counts
python -c "import sqlite3; c=sqlite3.connect('mem.db'); t=c.execute('SELECT COUNT(*) FROM memories').fetchone()[0]; w=c.execute('SELECT COUNT(*) FROM memories WHERE embedding IS NOT NULL').fetchone()[0]; print(f'total={t} with={w} without={t-w}')"

# 3. Diagnostics endpoint (server running)
curl http://localhost:8000/api/debug/embeddings

# 4. Health endpoint
curl http://localhost:8000/health

# 5. Memory recall trace after chat
curl http://localhost:8000/api/memory_trace

# 6. Unit tests
python -m pytest tests/test_memory_store.py -q
```

**Expected after full fix (env + sentence-transformers + backfill):**

- `embeddings_enabled: true`
- `embedding_model_loaded: true`
- `with_embedding: 917` (or current total)
- `without_embedding: 0`
- Recall trace `search_method: "vector_cosine"` for semantic queries

---

## Remaining Action Required (Operator)

1. **Set `EMBEDDINGS_ENABLED=true`** in environment (Replit Secrets / `.env` / shell).
2. **Install `sentence-transformers`** (add to `requirements.txt` for production deploy).
3. **Run `scripts/backfill_embeddings.py`** once to populate existing 917 rows.
4. **Restart uvicorn** so model loads at boot.

Without step 2, `embedding_model_loaded` stays `false` even with `EMBEDDINGS_ENABLED=true`.
