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

- A persistent AGI loop for continuous cognition  
- Multi-agent coordination (chat, scheduler, voice, messaging agents)  
- A memory service for long-term semantic context  
- A symbolic world model for structured reasoning  
- Goal agents for task and objective management  
- Real-world integrations (WhatsApp, email, CRM, notifications)  
- Autonomous workflows for lead handling and follow-ups  
- A deployable backend with live API and UI  

Together, these components behave as a unified cognitive system rather than a set of disconnected scripts.

---

## System Architecture

Key subsystems in this repository:

- `backend/agi/` — Core AGI loop, world model, memory service, goal agents  
- `backend/agents/` — Chat, intent, scheduler, voice, and messaging agents  
- `backend/integrations/` — WhatsApp, email, CRM, and notifier integrations  
- `backend/workflows/` — Autonomous task and business process flows  
- `memory/` — Persistent memory storage layer  
- `frontend/` — Web UI for interacting with the system  

These subsystems are wired together to support continuous cognition, memory-driven behavior, and autonomous task execution.

---

## Demo Capabilities

The hackathon demo showcases:

- Continuous AGI loop execution  
- Agent-based goal handling  
- Memory-assisted reasoning  
- World model state tracking  
- Autonomous workflows (lead, follow-up, meeting flows)  
- Real-world messaging and notification integrations  

This demonstrates a cognitive operating system approach rather than a single-task agent.

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

### Smoke Tests

Run the PowerShell smoke test script:

```powershell
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
