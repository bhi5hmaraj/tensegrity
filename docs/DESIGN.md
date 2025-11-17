# PadAI Design Document

**PadAI** (படை - "army" in Tamil): Multi-agent orchestration system for coordinating Claude Code agents via Beads task management.

## Problem Statement

When building complex software with multiple Claude Code agents working in parallel, we need a way to coordinate their work without conflicts. Each agent runs in a separate cloud session and needs to know what tasks are available, claim work, and report completion. The existing Beads CLI (`bd`) works great for single-agent workflows but has no built-in support for multi-agent coordination.

## Core Value Proposition

Enable multiple Claude Code agents (running in separate Anthropic cloud environments) to:
- Claim tasks from a shared Beads task graph without conflicts
- Update task status atomically
- Visualize progress in real-time via a web dashboard

## Architecture (MVP)

### The 80/20 Approach

We're building the **thinnest possible glue layer** between existing tools that already work. No custom state management, no complex distributed systems, no reinventing Beads.

```
┌─────────────────────────────────────┐
│  PadAI Dashboard (React + Vite)     │
│  • Upload .jsonl or poll server     │
│  • React Flow visualization         │
│  • Status filters, search           │
└─────────────────────────────────────┘
         ↓ HTTP GET /status (polls every 5s)

┌─────────────────────────────────────┐
│  PadAI Master Server (Express)      │
│  • Thin wrapper around bd CLI       │
│  • 3 endpoints: /status, /claim,    │
│    /complete                        │
│  • Single .beads/ folder (SSOT)     │
└─────────────────────────────────────┘
         ↑ HTTP POST /claim
         ↑ HTTP POST /complete
         │
    ┌────┴─────┬─────────┬─────────┐
    │          │         │         │
┌───┴───┐  ┌──┴──┐  ┌──┴──┐  ┌──┴──┐
│Agent 1│  │Ag 2 │  │Ag 3 │  │Ag N │
│Claude │  │Code │  │Web  │  │ ... │
└───────┘  └─────┘  └─────┘  └─────┘
```

### Components

#### 1. Master Server (~50 lines)

**Location:** `server/src/index.ts`

**Responsibilities:**
- Wrap `bd` CLI commands in HTTP endpoints
- Maintain single `.beads/` folder as source of truth
- Handle concurrent updates atomically (bd CLI already does this via file locking)

**API:**

```typescript
GET  /api/status
  → Returns: bd status --json output

POST /api/claim
  Body: { agentName: string }
  → Runs: bd ready --json
  → Takes first task, runs: bd update [id] --status in_progress --assignee [agentName]
  → Returns: claimed task object

POST /api/complete
  Body: { taskId: string, notes?: string }
  → Runs: bd update [taskId] --status completed --notes [notes]
  → Returns: { success: true }
```

**Why this works:**
- `bd` CLI already handles concurrent file access
- No need to reimplement Beads logic
- No database, no state management
- Literally just shelling out to an existing tool

#### 2. Dashboard (existing)

**Location:** `src/` (existing React app)

**Changes needed:**
- Add polling: `setInterval(() => fetch('/api/status'), 5000)`
- Parse response and update graph
- That's it

**Not needed for MVP:**
- WebSocket (polling is fine for personal use)
- Real-time animations
- Agent heartbeats

#### 3. Worker Agents

**No MCP server needed for MVP.** Workers use Claude's existing Bash tool:

```bash
# Claim task
TASK=$(curl -X POST https://padai.up.railway.app/api/claim \
  -H "Content-Type: application/json" \
  -d '{"agentName": "architect"}')

# Do work...

# Mark complete
curl -X POST https://padai.up.railway.app/api/complete \
  -H "Content-Type: application/json" \
  -d '{"taskId": "claude-24", "notes": "Server setup complete"}'
```

Simple, works today, no additional tooling.

## Deployment

### Railway (Recommended for MVP)

**Why Railway:**
- Push to GitHub, auto-deploy
- Free tier sufficient for personal use
- Supports custom binaries (bd CLI)
- Gets you a public URL immediately

**Setup:**

```dockerfile
# Dockerfile
FROM node:18-alpine

# Install bd CLI
RUN apk add --no-cache curl
RUN curl -L https://github.com/steveyegge/beads/releases/download/v0.1.0/bd-linux-amd64 \
    -o /usr/local/bin/bd && chmod +x /usr/local/bin/bd

WORKDIR /app
COPY server/package*.json ./
RUN npm install
COPY server/ .

EXPOSE 3000
CMD ["node", "src/index.js"]
```

Steps:
1. Push PadAI to GitHub
2. Connect Railway to repo
3. Railway auto-detects Dockerfile and deploys
4. Get URL: `padai-production.up.railway.app`

**Cost:** $0 (free tier)

## Real-Time Update Strategies (Post-MVP)

**Current Status (MVP):** Polling removed, manual refresh button added. This eliminates the 67s timeout and excessive load issues caused by 5-second polling.

For future real-time updates without polling, here's a comparison of options:

### Comparison Table

| Feature | WebSocket (Native) | Server-Sent Events (SSE) | Redis Pub/Sub (Self-hosted) | Redis Pub/Sub (Upstash) | Pusher (Managed) | Soketi (Self-hosted) |
|---------|-------------------|-------------------------|----------------------------|------------------------|------------------|---------------------|
| **Complexity** | Medium | Low | High | Medium | Very Low | Low-Medium |
| **Bidirectional** | ✅ Yes | ❌ No (server→client only) | ✅ Yes (via separate channels) | ✅ Yes | ✅ Yes | ✅ Yes |
| **Browser Support** | Excellent (all modern) | Excellent (all modern) | N/A (backend only) | N/A (backend only) | Excellent | Excellent |
| **Auto-reconnect** | Manual implementation | Built-in | Manual | Manual | Built-in | Built-in |
| **Setup Time** | ~2 hours | ~30 min | ~3 hours | ~15 min | ~15 min | ~1 hour |
| **Dependencies** | None (native) | None (native) | Redis server | None (serverless) | None (cloud) | Node.js server |
| **Cost (Monthly)** | $0 (included) | $0 (included) | $5-10 (DO/Vultr) | $0-8 (usage-based) | $0-49+ (usage-based) | $5-10 (DO/Vultr) |
| **Free Tier** | ✅ Unlimited | ✅ Unlimited | ❌ None | ✅ 10k commands/day | ✅ 200k msg/day | ❌ None |
| **Large Payloads** | ✅ Excellent | ⚠️ Good (see notes) | ✅ Excellent | ✅ Excellent | ✅ Excellent | ✅ Excellent |
| **Scalability** | Manual (sticky sessions) | Manual | Excellent (Redis cluster) | Excellent (global edge) | Automatic | Good (clustering support) |
| **Python Support** | ✅ FastAPI WebSocket | ✅ sse-starlette | ✅ redis-py | ✅ redis-py + upstash | ✅ pusher SDK | ✅ pusher-compatible |
| **Client Code** | ~20 lines | ~10 lines | N/A | N/A | ~5 lines | ~5 lines |
| **Ideal For** | Large graphs, bidirectional | Small-medium updates | Multi-server, large data | Serverless, global edge | Quick prototypes | Production without vendor lock |

### Detailed Analysis

#### 1. WebSocket (Native)

**Pros:**
- No external dependencies
- Full bidirectional communication
- Low latency
- Built into FastAPI

**Cons:**
- Requires reconnection logic
- Doesn't scale horizontally without sticky sessions or Redis
- More complex than SSE for one-way updates

**Best for:** Interactive features where clients need to send data back (task creation, live collaboration)

**Implementation estimate:** 2-3 hours

```python
# Server (FastAPI)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        # Send updates when tasks change
        await websocket.send_json({"type": "task_update", "data": tasks})
```

#### 2. Server-Sent Events (SSE)

**Pros:**
- Simple HTTP-based protocol
- Built-in reconnection
- Efficient for server→client updates
- Works through proxies/firewalls

**Cons:**
- One-way only (server→client)
- Connection limit per domain (6 in most browsers)
- Not suitable for bidirectional needs
- Large payloads can cause memory pressure (see handling strategies below)

**Best for:** Dashboard status updates, real-time logs, progress tracking

**Implementation estimate:** 30 minutes

**Handling Large Graphs with SSE:**

SSE can handle large payloads, but optimization is recommended:

1. **Differential Updates** (Recommended for large graphs)
   ```python
   # Send only changed tasks instead of full graph
   @app.get("/api/stream")
   async def stream_updates():
       last_state = {}
       async def event_generator():
           while True:
               current = {t['id']: t for t in get_all_tasks_fast()}

               # Send only changes
               added = [t for id, t in current.items() if id not in last_state]
               updated = [t for id, t in current.items()
                         if id in last_state and t != last_state[id]]
               removed = [id for id in last_state if id not in current]

               if added or updated or removed:
                   yield {
                       "event": "delta",
                       "data": json.dumps({
                           "added": added,
                           "updated": updated,
                           "removed": removed
                       })
                   }

               last_state = current
               await asyncio.sleep(2)
       return EventSourceResponse(event_generator())
   ```

2. **Compression** - Enable gzip compression in FastAPI/uvicorn
   ```python
   # Middleware for response compression
   from fastapi.middleware.gzip import GZipMiddleware
   app.add_middleware(GZipMiddleware, minimum_size=1000)
   ```

3. **Chunked Sending** - For initial load, send in batches
   ```python
   # Send full graph in chunks on initial connection
   yield {"event": "init_start", "data": json.dumps({"total": len(tasks)})}
   for chunk in chunks(tasks, 100):  # 100 tasks per chunk
       yield {"event": "init_chunk", "data": json.dumps(chunk)}
   yield {"event": "init_complete", "data": "{}"}
   ```

4. **Pagination** - For very large graphs (1000+ tasks)
   ```python
   # Client requests specific slice
   @app.get("/api/stream?offset=0&limit=100")
   ```

**Size Limits:**
- SSE has no spec-defined payload limit
- Practical limits:
  - **< 100 tasks**: Send full graph each update (simple, works fine)
  - **100-500 tasks**: Use differential updates
  - **500-1000 tasks**: Add compression + differential
  - **1000+ tasks**: Consider WebSocket or pagination

For PadAI's typical use case (< 100 concurrent tasks), **full graph updates work perfectly fine**.

```python
# Server (FastAPI + sse-starlette)
from sse_starlette.sse import EventSourceResponse

@app.get("/api/stream")
async def stream_updates():
    async def event_generator():
        while True:
            if tasks_changed:
                yield {"data": json.dumps(tasks)}
            await asyncio.sleep(1)
    return EventSourceResponse(event_generator())
```

```javascript
// Client
const eventSource = new EventSource('/api/stream');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateUI(data);
};
```

#### 3. Redis Pub/Sub (Self-hosted)

**Pros:**
- Excellent for multi-server setups
- Battle-tested at scale
- Can fan-out to WebSocket/SSE clients
- Decouples workers from dashboard

**Cons:**
- Requires Redis server ($5-10/mo)
- Adds architectural complexity
- Need to manage Redis instance
- Overkill for single-server MVP

**Best for:** Multi-region deployments, microservices, high-traffic scenarios

**Implementation estimate:** 3-4 hours

```python
# Worker publishes
redis_client.publish('task_updates', json.dumps(task))

# Server subscribes and broadcasts to WebSocket clients
pubsub = redis_client.pubsub()
pubsub.subscribe('task_updates')
for message in pubsub.listen():
    broadcast_to_websocket_clients(message['data'])
```

#### 4. Redis Pub/Sub (Upstash - Managed)

**Pros:**
- **Serverless** - no infrastructure to manage
- **Global edge network** - low latency worldwide
- **Pay-per-use** - only pay for what you use
- **Generous free tier** - 10,000 commands/day
- **REST API** - works in serverless environments (Cloud Run, Lambda)
- Same Redis protocol - drop-in replacement

**Cons:**
- Costs scale with usage (though cheaper than self-hosted initially)
- Vendor dependency (but Redis protocol, so portable)
- Cold starts if using REST API instead of native Redis protocol

**Best for:** Serverless deployments, Cloud Run/Lambda, global applications, MVP→production scaling

**Pricing:**
- **Free tier:** 10,000 commands/day (~300k commands/month)
- **Pay-as-you-go:** $0.2 per 100,000 commands
- **Pro (fixed):** $10/mo for 10M commands

**Comparison to self-hosted:**
```
Self-hosted Redis: $5-10/mo fixed + management time
Upstash:          $0-8/mo based on actual usage + zero management

For PadAI MVP with ~100 tasks, ~10 updates/hour:
- ~240 pub/sub operations/day
- ~7,200 operations/month
- Cost: $0 (within free tier)
```

**Implementation estimate:** 15 minutes (easier than self-hosted)

```python
# Using Upstash REST API (works in Cloud Run without persistent connections)
import httpx

UPSTASH_URL = "https://your-redis.upstash.io"
UPSTASH_TOKEN = "your-token"

# Worker publishes (HTTP POST instead of Redis connection)
async def publish_task_update(task):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{UPSTASH_URL}/publish/task_updates",
            headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"},
            json={"message": json.dumps(task)}
        )

# Server subscribes via WebSocket
import websockets
async def subscribe_upstash():
    uri = f"wss://your-redis.upstash.io/subscribe/task_updates"
    async with websockets.connect(uri, extra_headers={
        "Authorization": f"Bearer {UPSTASH_TOKEN}"
    }) as ws:
        async for message in ws:
            data = json.loads(message)
            broadcast_to_clients(data)
```

**Why Upstash for PadAI:**
- ✅ Perfect for Cloud Run (serverless-friendly)
- ✅ Free tier covers MVP usage
- ✅ Scales automatically as you grow
- ✅ No Redis server to maintain
- ✅ Global edge = fast updates worldwide

#### 5. Pusher (Managed Service)

**Pros:**
- Zero infrastructure setup
- Automatic scaling
- Built-in presence channels
- Generous free tier (100 concurrent connections, 200k messages/day)

**Cons:**
- Vendor lock-in
- Pricing scales with usage ($49/mo for 500 connections)
- Not self-hostable
- Adds external dependency

**Best for:** Rapid prototyping, startups, teams that don't want to manage infrastructure

**Pricing:**
- Free: 100 concurrent, 200k messages/day
- $49/mo: 500 concurrent, unlimited messages
- $299/mo: 2000 concurrent

**Implementation estimate:** 15 minutes

```python
# Server
import pusher
pusher_client = pusher.Pusher(app_id, key, secret, cluster)
pusher_client.trigger('tasks', 'update', {'data': tasks})
```

```javascript
// Client (3 lines!)
const pusher = new Pusher('key', {cluster: 'us2'});
const channel = pusher.subscribe('tasks');
channel.bind('update', (data) => updateUI(data));
```

#### 6. Soketi (Self-Hosted Pusher Alternative)

**Pros:**
- Pusher-compatible protocol (drop-in replacement)
- Self-hosted (full control, no vendor lock-in)
- High performance (uWebSockets.js - 10x faster than Socket.IO)
- Low resource usage (thousands of connections on 1GB/1CPU)
- Open source and free

**Cons:**
- Requires server infrastructure ($5-10/mo)
- Some setup complexity
- Maintenance concerns (less frequent updates recently)
- Need to manage updates and security

**Best for:** Production deployments, cost-conscious projects, avoiding vendor lock-in

**Pricing:**
- $0 software cost
- $5-10/mo VPS (DigitalOcean/Vultr)
- Unlimited connections/messages

**Implementation estimate:** 1-2 hours (setup + integration)

```bash
# Deploy on DigitalOcean/Vultr
docker run -p 6001:6001 quay.io/soketi/soketi:latest
```

```javascript
// Client (same as Pusher!)
const pusher = new Pusher('app-key', {
  wsHost: 'your-soketi-server.com',
  wsPort: 6001,
  forceTLS: false
});
```

### MVP Recommendation: **SSE for small graphs, Upstash + WebSocket for large**

**Decision Matrix:**

| Graph Size | Recommended Approach | Reason |
|------------|---------------------|---------|
| **< 100 tasks** | **SSE** (full graph) | Simple, $0, 30min setup, no optimization needed |
| **100-500 tasks** | **SSE** (differential) | Still cheap, add diff updates (~1hr total) |
| **500-1000 tasks** | **WebSocket** + compression | Better for frequent large updates |
| **1000+ tasks** | **Upstash + WebSocket** | Multi-server ready, serverless-friendly |

**Primary Recommendation for PadAI MVP: Server-Sent Events (SSE)**

**Why SSE for MVP:**

1. **Simplest implementation** - 30 minutes to add, no new dependencies
2. **Perfect fit for use case** - Dashboard only needs server→client updates
3. **Built-in reconnection** - Browser handles it automatically
4. **Zero cost** - No additional infrastructure
5. **Handles typical graphs** - For < 100 tasks, full graph updates work fine
6. **Easy to replace** - Can switch to WebSocket/Upstash later without major refactor

**Alternative: Upstash + WebSocket (for large graphs or multi-worker)**

If you expect:
- Large task graphs (500+ tasks)
- Multiple workers making frequent updates
- Global deployment with low latency requirements

Then skip SSE and go directly to **Upstash + WebSocket**:

```
Worker → Upstash Pub/Sub → Server WebSocket → Dashboard
```

**Pros:**
- ✅ Free tier covers MVP (10k commands/day)
- ✅ Serverless-friendly (perfect for Cloud Run)
- ✅ Handles large payloads without optimization
- ✅ Decouples workers from server (workers publish to Redis, don't hit server)
- ✅ Multi-server ready from day one

**Setup time:** ~1 hour (vs 30min for SSE)

**Migration path:**
```
Option A (Simple): Manual refresh → SSE (Phase 2) → WebSocket/Upstash (if needed)
Option B (Scale-ready): Manual refresh → Upstash + WebSocket (Phase 2)
```

**When to upgrade from SSE:**

- **→ WebSocket:** When you need bidirectional (task creation from dashboard) OR graphs > 500 tasks
- **→ Upstash:** When you have multiple workers OR need multi-server OR global deployment
- **→ Soketi:** When you want Pusher-like features without vendor lock-in
- **→ Pusher:** Quick prototype, willing to pay for convenience

**Implementation priority:**

1. **Now (MVP):** Manual refresh button ✅ **DONE**
2. **Next (Phase 2):** Add SSE for real-time updates (~30 min) **OR** Upstash if expecting large scale
3. **Future (Phase 3+):** Upgrade to WebSocket/Upstash if SSE limitations hit

### Code Example: SSE Implementation

**Server (add to server/main.py):**

```python
from sse_starlette.sse import EventSourceResponse
import asyncio
import json

# Track last known state
_last_task_hash = None

@app.get("/api/stream")
async def stream_updates(request: Request):
    """Stream task updates via Server-Sent Events"""
    async def event_generator():
        global _last_task_hash
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                break

            # Get current tasks
            try:
                tasks = get_all_tasks_fast(WORKSPACE)
                task_hash = hash(json.dumps(tasks))

                # Only send if changed
                if task_hash != _last_task_hash:
                    _last_task_hash = task_hash
                    yield {
                        "event": "update",
                        "data": json.dumps({"tasks": tasks})
                    }
            except Exception as e:
                logger.error(f"SSE error: {e}")

            await asyncio.sleep(2)  # Check every 2 seconds

    return EventSourceResponse(event_generator())
```

**Client (update frontend/src/App.tsx):**

```typescript
useEffect(() => {
  fetchData(); // Initial load

  // Connect to SSE stream
  const eventSource = new EventSource(`${API_URL}/api/stream`);

  eventSource.addEventListener('update', (event) => {
    const data = JSON.parse(event.data);
    setTasks(data.tasks || []);
    if (debug) console.log('[SSE] Task update:', data);
  });

  eventSource.onerror = (err) => {
    console.error('[SSE] Connection error:', err);
    eventSource.close();
    // Fallback to manual refresh if SSE fails
  };

  return () => eventSource.close();
}, []);
```

## What We're NOT Building (Yet)

These are intentionally deferred until we've validated the core concept:

- **Advanced real-time (WebSocket/Pusher/Soketi)** - SSE is sufficient for dashboard updates. Add if we need bidirectional or multi-server.
- **MCP server for workers** - Bash + curl works. Build MCP if workflow feels clunky after using it.
- **Telegram notifications** - Can add in 20 lines once we know what events matter.
- **Agent registry / heartbeats** - Not needed until agents start disappearing and we need monitoring.
- **Authentication** - Personal project, no sensitive data. Add if deploying publicly.
- **Horizontal scaling** - One server handles this easily. Cross that bridge if we hit it.

## Success Metrics

MVP is successful if:
1. 3+ Claude agents can simultaneously claim different tasks without conflicts
2. Dashboard updates within 5 seconds of task status changes
3. We can build a real project (e.g., multiplayer Pac-Man) using this system
4. Total setup time from git clone to working: < 30 minutes

## Development Phases

### ✅ Phase 1: Simple MVP (COMPLETED)

**Goal:** Validate the concept with the simplest possible implementation.

**What we built:**
- **Backend:** FastAPI server (Python) wrapping bd CLI
  - `server/beads.py` - Python wrapper for bd CLI operations
  - `main.py` - FastAPI server with 5 HTTP endpoints
  - Endpoints: `/api/status`, `/api/ready`, `/api/tasks`, `/api/claim`, `/api/complete`
  - Uses `bd --no-db` mode for JSONL-only operation

- **Frontend:** React + TypeScript + Vite
  - React Flow visualization with Dagre layout
  - Real-time polling (5 second interval)
  - Dark theme UI with status color coding
  - Mini-map and controls for navigation

- **Worker Integration:** Simple curl commands
  - `docs/docs/WORKER_GUIDE.md` - Complete guide for worker agents
  - `scripts/test-agent.sh` - Bash script for testing workflows
  - No MCP needed - just HTTP + curl

- **Deployment:** Docker + Cloud Run ready
  - `Dockerfile` - Multi-stage build with bd CLI
  - (Deprecated) `railway.json` - One-click Railway deployment

**Stack choices:**
- Python instead of Express (better alignment with beads-mcp for Phase 2)
- FastAPI for async + automatic docs
- React Flow for dependency graph visualization

**Status:** ✅ Tested and working
- Task claim/complete workflow verified
- Dependency graph visualization working
- Ready for multi-agent testing

**Time spent:** ~4 hours

### 🔄 Phase 2: Explore beads-mcp Integration (PLANNED)

**Goal:** Investigate if we can leverage existing beads-mcp infrastructure instead of building from scratch.

**Background:**
The Beads ecosystem already has `beads-mcp` (https://github.com/steveyegge/beads/tree/main/integrations/beads-mcp), which provides:
- FastMCP server wrapping bd CLI with ~20 tool functions
- Agent Mail for inter-agent HTTP messaging
- Persistent context storage across MCP requests
- Remote access via Streamable HTTP transport

**Key question:** Can we extend/reuse beads-mcp instead of maintaining parallel infrastructure?

**Investigation tasks:**

1. **Understand beads-mcp architecture**
   - How does Agent Mail work?
   - What's the daemon doing?
   - Can we use remote MCP transport for workers?
   - Read: `/beads/integrations/beads-mcp/src/beads_mcp/`

2. **Compare approaches:**
   ```
   Current (Phase 1):     Proposed (Phase 2):
   ┌─────────────┐        ┌─────────────┐
   │ PadAI HTTP  │        │ beads-mcp   │
   │ FastAPI     │   vs   │ FastMCP     │
   │ bd CLI      │        │ bd tools    │
   └─────────────┘        └─────────────┘
   ```

3. **Evaluate options:**

   **Option A: Extend beads-mcp**
   - Fork/PR to add multi-agent coordination
   - Add HTTP endpoints on top of MCP
   - Pros: Leverage existing tools, stay in sync with Beads
   - Cons: Coupling to beads-mcp development

   **Option B: Import beads-mcp tools**
   - Keep PadAI FastAPI server
   - Import `from beads_mcp.tools import *`
   - Add thin HTTP layer on top
   - Pros: Reuse battle-tested code, control our API
   - Cons: Still some duplication

   **Option C: Remote MCP wrapper**
   - Run beads-mcp as remote MCP server
   - PadAI becomes HTTP→MCP proxy
   - Workers use native MCP protocol
   - Pros: Clean separation, MCP native
   - Cons: Extra abstraction layer

4. **MCP for workers (instead of curl)**
   - Expose PadAI as remote MCP server
   - Workers use MCP tools: `mcp__padai__claim_task`, `mcp__padai__complete_task`
   - Much cleaner than curl in agent workflows
   - FastMCP makes this trivial to add

5. **Agent Mail integration**
   - Investigate beads-mcp Agent Mail for inter-agent messaging
   - Could replace Telegram bot idea
   - HTTP-based, simple protocol

**Deliverables:**
- Decision document: Which option to pursue
- POC implementation if Option B/C chosen
- Updated worker guide with MCP instructions

**Time estimate:** 2-3 hours investigation + 3-4 hours implementation

### Phase 3: Polish & Real-World Testing (PLANNED)

**Goal:** Use PadAI to build a real project and fix pain points.

**Tasks:**
- Deploy to Railway with real .beads/ project
- Have 3-4 Claude agents build something real (multiplayer Pac-Man?)
- Identify bottlenecks and UX issues
- Add WebSocket if polling feels slow
- Add Telegram bot if coordination needs human oversight

**Success criteria:**
- Agents successfully collaborate without conflicts
- Dashboard clearly shows progress
- Total coordination overhead < 10% of dev time

**Time estimate:** 1 day of testing + fixes

### Phase 4: Production Hardening (FUTURE)

Only if PadAI gets regular use:
- Authentication & multi-tenancy
- Monitoring & logging
- Horizontal scaling
- Task assignment strategies
- Web UI for task creation

## Open Questions

1. **How do we initialize .beads/ on the server?**
   - Option A: Git clone a project repo that has .beads/
   - Option B: Start with empty .beads/, let workers create tasks via API
   - **Decision: Option A for MVP** - simpler, we already have beads repos

2. **Should dashboard be served from same Express server or separate?**
   - **Decision: Same server** - simpler deployment, one Railway service

3. **How to handle bd CLI errors (task not found, invalid status, etc.)?**
   - **Decision: Return error to caller** - let workers handle retries

## Technical Risks

**Risk 1: Concurrent bd updates cause conflicts**
- Mitigation: bd uses file locking, should handle this
- Fallback: Add simple mutex in Express if needed

**Risk 2: Railway free tier limits**
- Mitigation: Monitor usage, upgrade to $5/mo plan if needed
- Alternative: Switch to Fly.io or DigitalOcean

**Risk 3: Polling creates too much load**
- Mitigation: Start with 5s interval, increase if needed
- Fallback: Add WebSocket if polling becomes problematic

## Future Enhancements (Post-MVP)

Once the MVP proves valuable, consider:

- MCP server for cleaner worker integration (no manual curl commands)
- WebSocket for sub-second dashboard updates
- Telegram bot for notifications on critical events
- Agent registry showing which agents are alive and what they're working on
- Task assignment strategies (load balancing, priority-based claiming)
- Web UI for creating tasks (not just visualizing)
- Export execution logs/analytics

## Success Stories

The first real test will be building the **Multiplayer Pac-Man** game we prototyped, using PadAI to coordinate:
- ARCHITECT agent (design work)
- NEXUS agent (server implementation)
- PHANTOM agent (maze system)
- VOLT agent (ghost AI)

If these 4 agents can successfully collaborate to build a working game without stepping on each other, PadAI is validated.

---

**Author:** Built collaboratively with Claude Code
**Date:** 2025-11-15
**Status:** Design approved, ready for implementation
