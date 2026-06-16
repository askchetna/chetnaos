# ChetnaOS — Cognitive Operating System for AGI (Hackathon Build)

ChetnaOS is an architecturally integrated cognitive operating system designed to explore artificial general intelligence through system-level intelligence, not just isolated models.

This repository contains a unified platform combining agents, memory, world modeling, goal management, and real-world integrations into a single evolving cognitive system.

🏆 Hackathon Build — ChetnaOS AGI Architecture Demo

---

## Vision

Most AI systems today are collections of tools and models. ChetnaOS is designed as an operating system for intelligence — where cognition, memory, goals, and actions are coordinated through a shared system architecture.

The focus is on architectural completeness and integration rather than brute-force training.

---

## What ChetnaOS Does

ChetnaOS provides:

- A **developmental cognitive cycle** (26 stages, including DECIDE) via `src/chetnaos/cycle/`
- Single runtime entry via `src/chetnaos/runtime/` and `backend/runtime.py`
- Persistent memory through `MemoryStore` with unified item schema (confidence, source, decay)
- Constitution-grounded reasoning via `PromptBuilder` (`src/chetnaos/reasoning/`)
- Reality verification → **DECIDE** → Embodiment output path
- Mandatory `CycleTrace` per cycle (cycle_id, stage timing, context flags)
- Tool agent (calculator, web search, fetch) at `/api/agent` through organism
- Kalpavriksha domain plugin at `backend/plugins/kalpavriksha/` (`/evaluate`, `/roi`, `/crop`)
- Deployable FastAPI v3 backend with dashboard UI

---

## System Architecture (v3 — live)

| Layer | Path | Role |
|-------|------|------|
| HTTP shell | `backend/app.py` | FastAPI v3 entry |
| Runtime singleton | `backend/runtime.py` | One `ChetnaRuntime` per process |
| Cognitive cycle | `src/chetnaos/cycle/cognitive_cycle.py` | 26-stage organism loop |
| Runtime core | `src/chetnaos/runtime/` | State machine, sleep manager |
| Reasoning | `src/chetnaos/reasoning/` | PromptBuilder, LLM router |
| Memory kernel | `src/chetnaos/memory_kernel/` | Schema + MemoryStore facade |
| Organs | `src/chetnaos/organs/` | 25 cognitive organ shims → implementations |
| Compat shims | `src/chetnaos/orchestrator/` | 7D1 — removed in 7D2 when green |
| Plugins | `backend/plugins/kalpavriksha/` | Land/crop/ROI domain tools |
| Constitution | `src/chetnaos/constitution/` | Mission, values, ethics |

**Validation:**
```powershell
python scripts/phase7_gate.py
```

See `PHASE7_RULES.md` and `report.md` for migration status.

---

## Demo Capabilities

The live demo showcases:

- Full cognitive cycle on `/api/chat` and `/api/goal`
- Memory-assisted reasoning (vector recall when embeddings enabled)
- Dashboard at `/dashboard` and `/api/dashboard`
- Agent tools at `/api/agent`
- Kalpavriksha calculators via `/evaluate`, `/roi`, `/crop`

---

## Quickstart (Local)

### Setup Environment

```bash
cp env.example .env
# Edit .env and replace _PUT_YOUR_KEY_HERE_ with your actual GROQ_API_KEY
```

### 2) Install Dependencies

```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1  # PowerShell on Windows
pip install -r requirements.txt
```

### 3) Run Locally

```powershell
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

- Open `http://127.0.0.1:8000/` for the UI
- Health check: `http://127.0.0.1:8000/health` should return a JSON payload similar to:

  ```json
  {
    "ok": true,
    "status": "ok",
    "service": "ChetnaOS",
    "light_mode": true,
    "embeddings_enabled": false,
    "model": "llama-3.1-8b-instant"
  }
  ```
- API docs: `http://127.0.0.1:8000/docs`

## Agent Usage Examples

### Calculator Tool
- `calc: (23+7)*4`
- `calculate 2**10 + 5`

### Web Search Tool
- `search latest AI news`
- `search python fastapi tutorial`

### Web Fetch Tool
- `web: https://example.com/article`
- `web: https://news.ycombinator.com`

### Chat Mode
- Regular conversation with Groq LLM

## Memory System (Light Mode Friendly)

ChetnaGPT includes a persistent memory system using SQLite storage.

- **Semantic Search (optional)**: Uses sentence-transformers for similarity matching when enabled.
- **Graceful Fallback**: Works without embeddings packages (memory search disabled, app still runs).
- **SQLite Storage**: Persistent across restarts.

In default `LIGHT_MODE` the embedding-backed semantic search is disabled so the
app boots fast and can run on Railway’s free tier. Agent behaviour remains
functional, but without semantic recall.

## Project Structure

```
backend/
  app.py
  agent.py
  memory.py
  config.py
memory/
  db.py
frontend/
  index.html
  app.js
Procfile
requirements.txt
runtime.txt
env.example
smoke.ps1
```

## Testing

### Phase 1 Gate (required before Phase 2)

```powershell
python scripts/phase1_gate.py
```

Runs: import test, memory persistence test, API health test (TestClient).

### Smoke Tests (requires running server)

```powershell
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
.\smoke.ps1
```

This tests:
- `/health` endpoint
- `/api/chat` endpoint (empty message)
- `/api/agent` endpoint (search demo)
- `/api/mem/add` and `/api/mem/search` endpoints

### Manual API Testing

PowerShell (Windows):

```powershell
# Test health endpoint
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get

# Test chat endpoint
$body = @{ message = "Ping" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/chat -ContentType "application/json" -Body $body

# Test agent endpoint
$body = @{ message = "Search latest AI news (3 bullets)" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/agent -ContentType "application/json" -Body $body
```

## Deploy to Railway

1. Create a new project on Railway and select "Deploy from GitHub".
2. Push this repository to GitHub and connect it to Railway.
3. Railway will detect the `Procfile` and start the web service.
4. Set the service to use `Python 3.11` if prompted (also in `runtime.txt`).
5. Add environment variables: `GROQ_API_KEY` (required), `GROQ_MODEL` (optional).
6. Once deployed, open the service URL. `/health` should return `{ "ok": true, "model": "..." }`.

## Railway Deploy

- Variables:
  - `GROQ_API_KEY` (required for LLM features, optional for basic boot)
  - `GROQ_MODEL` (optional, defaults to `llama-3.1-8b-instant`)
  - `LIGHT_MODE` (optional, default `true`; set to `false` to enable heavy features)
  - `EMBEDDINGS_ENABLED` (optional override; when unset it is `false` in LIGHT_MODE and `true` otherwise)
- Start Command: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
- After deploy: Generate Domain → test `/health` and open the root UI.

## Notes

- CORS is enabled for all origins by default.
- The root route `/` serves `frontend/index.html`.
- Environment variables are loaded from `.env` file.
- Supports both Chat Mode (direct LLM) and Agent Mode (with tool routing).
- **Keep secrets only in .env file (not committed to git).**
- Agent tools: calculator, web search, web fetch, and LLM chat.
