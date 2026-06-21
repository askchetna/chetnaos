# ChetnaOS

A cognitive operating system: one runtime, one cycle, persistent memory, constitution-grounded reasoning.

## Vision

Most AI systems are collections of tools. ChetnaOS coordinates cognition, memory, goals, and action through a single developmental architecture — studying how repeated interaction reshapes memory, beliefs, identity, and behavior over time.

## Architecture

```
backend/          FastAPI HTTP shell
frontend/         Chat + dashboard UI
src/chetnaos/
  runtime/        ChetnaRuntime singleton, state machine, sleep
  cycle/          27-stage cognitive cycle + trace
  memory/         Working memory, store, schemas, identity guard
  cognition/      Executive, goals, beliefs, emotion, curiosity, self-model
  reasoning/      PromptBuilder, LLM router, honesty guard
  organism/       Perception, memory recall, learning, sleep, identity, reality
  tools/          Calculator, web search, fetch (agent mode)
  constitution/   Mission, values, ethics, dharma rules
  dashboard/      Runtime snapshots for telemetry UI
memory/           SQLite vector store + embedding config
tests/            Pytest suite
```

## Request flow

```
POST /api/chat
  → ChetnaRuntime.process()
    → CognitiveCycle.run()
      → recall memory → build context → LLM reasoning
      → reflect, update beliefs, sleep (every N cycles)
      → ResponseComposer → reply
```

## Quickstart

```bash
cp env.example .env
pip install -r requirements.txt
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

Open `http://127.0.0.1:8000` for chat, `/dashboard` for cognitive telemetry.

## API

| Endpoint | Purpose |
|----------|---------|
| `POST /api/chat` | Chat with memory + cycle |
| `POST /api/agent` | Chat + tools (calc, web) |
| `POST /api/goal` | Add user goal |
| `GET /api/dashboard` | Cognitive telemetry |
| `GET /health` | Health check |

## Environment

| Variable | Purpose |
|----------|---------|
| `GROQ_API_KEY` | LLM API key |
| `GROQ_MODEL` | Model name |
| `LIGHT_MODE` | Default `true` — set `EMBEDDINGS_ENABLED=true` for vector recall |

## Tests

```bash
python -m pytest tests/ -q
```
