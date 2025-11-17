# PadAI — Multi‑Agent Orchestration (FastAPI + React Flow)

PadAI coordinates multiple worker agents on a shared task graph stored in Beads (.beads/issues.jsonl). The backend is Python/FastAPI; the frontend is React/TypeScript. Deployments target Cloud Run with Cloud Build triggers for preview and main.

## Repo Layout

- server/ — Python backend (FastAPI) and bd CLI wrapper
- frontend/ — React UI (Vite) with React Flow graph
- infra/ — Terraform + Cloud Build triggers for Cloud Run
- docs/ — design notes, worker guide, Cloud Run docs
- scripts/ — helper scripts (run server, worker loop, test agent)

## Architecture

```
┌─────────────────┐            same‑origin (prod)
│  React Frontend │  ────────────────►  / (served by FastAPI)
│   (Vite/React)  │            dev: http://localhost:3000 → API_URL
└────────┬────────┘
         │  REST /api/*
┌────────▼────────┐  reads/writes
│  FastAPI (Py)   │ ────────────────►  .beads/issues.jsonl (via bd CLI)
│  server/main.py │
└────────────────┘
```

## Quick Start

### 1) Install bd CLI

```bash
curl -L https://github.com/steveyegge/beads/releases/latest/download/bd-linux -o /usr/local/bin/bd
chmod +x /usr/local/bin/bd
```

### 2) Run locally

```bash
# Python 3.10–3.13
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel

# Install backend deps
pip install -r server/requirements.txt

# Option A: Build FE + run API on :8000
./scripts/run_server.sh

# Option B: API only (expects frontend/dist already built)
python -m server.main
```

- API/FE on http://localhost:8000 when using Option A (same‑origin)
- Note: pydantic 2.9+ is pinned for Python 3.13 compatibility

### 3) Frontend dev (optional)

```bash
cd frontend
npm install
npm run dev  # http://localhost:3000
```

By default the FE uses same‑origin in production and `VITE_API_URL` in dev. To point dev at the API:

```bash
# frontend/.env.local
VITE_API_URL=http://localhost:8000
```

### 4) Seed Beads data

```bash
# In your workspace containing .beads/
bd init
bd create "Task 1" --status ready
bd create "Task 2" --status ready
bd dep add task-2 task-1 --type blocks
```

## API Endpoints

### GET /api/status

```bash
curl http://localhost:8000/api/status
```

### GET /api/ready

```bash
curl http://localhost:8000/api/ready
```

### GET /api/tasks

```bash
curl http://localhost:8000/api/tasks
```

### POST /api/claim

```bash
curl -X POST http://localhost:8000/api/claim   -H "Content-Type: application/json"   -d '{"agent_name": "agent-1"}'
```

### POST /api/complete

```bash
curl -X POST http://localhost:8000/api/complete   -H "Content-Type: application/json"   -d '{"task_id": "padai-4"}'
```

### POST /api/create

```bash
curl -X POST http://localhost:8000/api/create   -H "Content-Type: application/json"   -d '{
    "title": "Platformer MVP: Scaffold",
    "description": "Single HTML + canvas with basic movement",
    "issue_type": "task",
    "priority": 2,
    "labels": ["game", "platformer"],
    "assignee": "littleboy"
  }'
```

### POST /api/update

```bash
curl -X POST http://localhost:8000/api/update   -H "Content-Type: application/json"   -d '{
    "task_id": "padai-42",
    "status": "in_progress",
    "assignee": "littleboy",
    "priority": 1,
    "title": "Platformer MVP: Basic Movement"
  }'
```

## 🤖 For Worker Agents

See **docs/WORKER_GUIDE.md** for the complete guide.

### Quick Start

```bash
export PADAI_MASTER="http://localhost:8000"
export AGENT_NAME="worker-$(date +%s)"

# Claim
task=$(curl -s -X POST $PADAI_MASTER/api/claim -H 'Content-Type: application/json' -d '{"agent_name":"'$AGENT_NAME'"}')

# Complete
id=$(echo "$task" | jq -r .task.id)
curl -s -X POST $PADAI_MASTER/api/complete -H 'Content-Type: application/json' -d '{"task_id":"'$id'"}'
```

See `scripts/test-agent.sh` and `scripts/worker-loop.sh` for full examples.

## Configuration

Backend:
- `WORKSPACE_PATH` — absolute path containing `.beads/` (default: CWD)
- `LOG_LEVEL` — `DEBUG` | `INFO` | `WARNING` (default: `INFO`)
- `PORT` — bind port for uvicorn (default: `8000`)

Frontend:
- `VITE_API_URL` — dev‑only override for API base URL (default: same‑origin)

The server auto‑loads `.env.local` (then `.env`) at startup.

## Deployment (Cloud Run)

Use `scripts/deploy_cloud_run.sh <PROJECT> <REGION> <SERVICE>` for direct gcloud deployment.

Terraform can be added later for team/production scenarios (optional). See docs/CLOUD_RUN.md for details.

## Docker (local)

```bash
docker build -t tensegrity-server .
docker run -p 8000:8000 -v /path/to/workspace:/workspace tensegrity-server
```

## Roadmap
- Remote MCP instead of curl
- Agent Mail for inter-agent communication
- Integration with beads-mcp tools
- WebSocket for real-time updates
- Telegram bot integration
- Authentication & multi-tenancy

## License
MIT
