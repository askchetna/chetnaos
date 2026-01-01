# Chetna-GPT Agent v0.2

Minimal FastAPI backend + vanilla JS frontend with real tools, deployable on Railway.

## Quickstart

### 1) Setup Environment

Copy the example environment file and add your Groq API key:

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
- Health check: `http://127.0.0.1:8000/health` should return `{ "ok": true, "model": "..." }`
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

## Memory System

ChetnaGPT includes a persistent memory system using sentence embeddings and SQLite storage.

### Memory Endpoints

#### Add Memory
```powershell
$body = @{ text = "Your memory text here"; meta = @{ source = "user" } } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/mem/add -ContentType "application/json" -Body $body
```

#### Search Memory
```powershell
$body = @{ query = "search query"; k = 5 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/mem/search -ContentType "application/json" -Body $body
```

### How Memory Works

- **Automatic Context**: Chat and Agent responses include relevant memories as context
- **Semantic Search**: Uses sentence-transformers for similarity matching
- **Graceful Fallback**: Works without embeddings package (memory disabled)
- **SQLite Storage**: Persistent across restarts

### Memory Integration

When you chat with ChetnaGPT, it automatically:
1. Searches memory for relevant context
2. Includes top 3 matches in system prompt
3. Provides more contextual responses

Example:
```powershell
# Add a memory
$body = @{ text = "User prefers concise responses" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/mem/add -ContentType "application/json" -Body $body

# Chat will now consider this preference
$body = @{ message = "Tell me about AI" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/chat -ContentType "application/json" -Body $body
```

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

- Variables: `GROQ_API_KEY` (required), `GROQ_MODEL` (optional)
- Start Command: `uvicorn backend.app:app --host 0.0.0.0 --port ${PORT}`
- After deploy: Generate Domain → test `/health` and open the root UI.

## Notes

- CORS is enabled for all origins by default.
- The root route `/` serves `frontend/index.html`.
- Environment variables are loaded from `.env` file.
- Supports both Chat Mode (direct LLM) and Agent Mode (with tool routing).
- **Keep secrets only in .env file (not committed to git).**
- Agent tools: calculator, web search, web fetch, and LLM chat.
