# Deployment (single Dockerfile)

This project uses a single Dockerfile at repo root for everything:
- Local smoke tests
- CI/CD builds (GitHub Actions)
- Cloud Run deployment

See:
- docs/CLOUD_RUN.md for Cloud Run deploy and CI/CD details
- scripts/docker_smoke.sh to build and run locally with health checks

Quick local test:
```bash
scripts/docker_smoke.sh           # builds image, runs on :8000, hits /api
scripts/docker_smoke.sh --keep    # keep container running after checks
```

Environment:
- The container exposes 8080 and respects `$PORT` at runtime (Cloud Run default).
- bd is installed via the official Beads installer; bd is required at runtime.
- WORKSPACE_PATH defaults to `/workspace` and the Dockerfile copies `.beads` into `/workspace/.beads`.

No other Dockerfiles or compose files are supported. The pre-push hook enforces a single root Dockerfile to prevent drift.

---

## Cloud Run (Recommended)

See docs/CLOUD_RUN.md for a step-by-step guide using Artifact Registry and Cloud Run. The Dockerfile builds the frontend and serves it from FastAPI, honors `$PORT`, and seeds `/workspace/.beads` during build.

---

## Local Development

To run without Docker during development, use:

```bash
# Backend
python -m venv .venv && source .venv/bin/activate
pip install -r server/requirements.txt
python -m server.main  # http://localhost:8000

# Frontend
cd frontend && npm install && npm run dev  # http://localhost:3000
```

---

## Docker manual

Manual build/run using the single Dockerfile:

```bash
docker build -t tensegrity-server .
docker run -p 8000:8080 tensegrity-server
```

---

## Notes
- No docker-compose variant provided to avoid drift.

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | 3000 |
| `WORKSPACE_PATH` | Path to project with .beads/ | Current directory |
| `NODE_ENV` | Environment (development/production) | development |

---

## Troubleshooting

### "bd: command not found"
Install bd CLI:
```bash
curl -L https://github.com/steveyegge/beads/releases/download/v0.1.0/bd-linux-amd64 \
  -o /usr/local/bin/bd
chmod +x /usr/local/bin/bd
```

### "No beads database found"
Make sure `.beads/` folder exists in WORKSPACE_PATH:
```bash
cd /path/to/your/project
ls .beads/issues.jsonl  # Should exist
```

### CORS errors from dashboard
Server has CORS enabled by default. If issues persist, check browser console and verify the server URL.

---

## Next Steps

Once deployed:
1. Update dashboard to poll your server URL
2. Create worker slash commands pointing to your endpoint
3. Test with 2-3 agents claiming tasks
4. Monitor via Railway logs or `docker logs`
