# 🧠 AGENTS.md — Donkey Workspace (Root)

This repository combines a Django backend and a React/Vite frontend. The root `AGENTS.md` keeps repo-wide goals. Backend and frontend specifics live in their own `AGENTS.md` files.

## 📌 Repo-Wide Goals

- Document the overall architecture linking the backend API and the UI.
- Keep backend and frontend routes in sync.
- Add integration tests that cover end-to-end assistant flows.
- Reference the roadmaps in `backend/docs/` for longer-term plans.

## 🔗 Sub-Project Guides

- **Backend tasks:** `backend/AGENTS.md`
- **Frontend tasks:** `frontend/AGENTS.md`

# AGENTS.md

## 🧠 Project Overview

This repo powers an intelligent assistant framework composed of:

- **Assistants** — personalized LLM personas that reflect, delegate, and evolve.
- **Agents** — low-level task executors spun up by Assistants.
- **MCP Core** — the orchestration layer (Model Context Protocol).
- **Embeddings** — vector search for memory/context recall.
- **Intel Core** — document ingestion (PDFs, URLs, YouTube) + smart chunking.
- **Frontend** — React/Vite dashboard for interacting with Assistants and reflections.

---

## 📆 Current Focus

We are entering **Phase 3: Delegation + Document Intelligence**.

### ✅ What's working:

- Assistant creation, projects, thoughts, reflections, and delegation events.
- DevDashboard document explorer.
- Assistant chat, memory logging, and token usage tracking.
- Codex integrated and actively managing PRs with validated tasks.

### 🛠️ In Progress:

- Codex fixing DevDoc reflection failures (due to missing linked `Document`)
- Continuing end-to-end context tracing across assistants, thoughts, threads.

---

## 🧪 Task Queues

### Assistant Pipeline

- [ ] Finalize `AssistantTranscriptView`
- [ ] Complete `DelegationEvent` explorer
- [ ] Build `SpawnAssistantFromThought` UX
- [ ] Route assistant reflections to thread/project context

### DevDocs + Reflections

- [ ] Codex: Fix DevDoc ↔ Document linking fallback
- [ ] Codex: Cleanup failed reflection retries
- [ ] Add UI for grouped reflections by tag/topic

### Core Infrastructure

- [ ] Add automated `flush_chat_sessions` weekly
- [ ] Auto-archive unused agents
- [ ] Add `/status` health check endpoints

---

## 🔧 Developer Setup

```bash
cd backend/
make run         # Starts Django, Redis, and Celery

cd ../frontend/
npm install
npm run dev      # Starts Vite UI
```

⚙️ Optional Scripts

# Run seeders

python manage.py seed_assistants
python manage.py seed_documents
python manage.py reflect_on_all_devdocs

# Check embedding + flush sessions

python manage.py check_embedding_status
python manage.py flush_chat_sessions

🧠 Notes for Codex
• Use capabilities/ for any new assistant-powered modules.
• Embed all text data using generate_embedding() and save_embedding().
• Store delegation events in DelegationEvent, link to ChatSession, MemoryEntry, and Project.
• Use narrative_thread to group assistants across multi-stage thoughts.
• Recent APIs expose assistant memories and allow instant reflection or spawning from any context.

⸻
