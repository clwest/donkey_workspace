# AGENTS.md

## 🧠 Assistant Delegation + Control System

This repository implements a dynamic assistant-agent orchestration framework, where top-level Assistants can create agents, spawn sub-assistants, and reflect on memory autonomously. Codex is used to extend and maintain this ecosystem.

---

## 💡 Key Concepts

### Assistants

- Core AI entities with personality, tone, and specialty
- Backed by a `system_prompt` and linked documents
- Can spawn other assistants or agents

### Agents

- Task-specific executors (e.g. research agent, coder agent)
- Typically short-lived and delegated by Assistants

### Projects

- Used to organize objectives, tasks, milestones, and reflections
- Each AssistantProject can include memory chains, thoughts, and linked documents

### Memory

- Conversation and action logs saved as `MemoryEntry`
- Indexed by vector search using PGVector + OpenAI embeddings
- Memory chains and related reflections can be visualized per assistant

### Reflections

- Logged when assistants reflect on memory, decisions, or context
- Can be manually triggered or auto-triggered during delegation

### Delegation

- Assistants can create sub-assistants with a reason and summary
- DelegationEvents are tracked in the database and visible via API

---

## 🔌 Directory Structure

```bash
backend/
├── assistants/           # Assistant models, serializers, views, and helper functions
├── agents/               # Lightweight agents for assistant task delegation
├── intel_core/           # Handles document ingestion, tagging, and embedding
├── memory/               # Memory entry system, feedback, and threading
├── mcp_core/             # Core logic for reflections, threading, assistant bootstrapping
├── prompts/              # Prompt templates and mutation tools
├── project/              # Project, Objective, Task, and Milestone models
├── embeddings/           # PGVector integration, chunking, and retrieval
└── server/               # Django settings, URLs, Celery setup
```

---

## 🛠️ Setup Commands

```bash
# Backend
cd backend
make run        # starts Django + Celery

# Frontend
cd frontend
npm install
npm run dev
```

---

## 🧪 Management Commands

```bash
# DevDoc and embedding management
python manage.py reflect_on_all_devdocs
python manage.py embed_assistants
python manage.py embed_devdocs

# Session flushing
python manage.py flush_chat_sessions

🧠 Notes for Codex
• Use capabilities/ for any new assistant-powered modules.
• Embed all text data using generate_embedding() and save_embedding().
• Store delegation events in DelegationEvent, link to ChatSession, MemoryEntry, and Project.
• Use narrative_thread to group assistants across multi-stage thoughts.

⸻
```
