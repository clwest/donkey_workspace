# 🧠 Donkey Workspace

This is the unified monorepo powering the Donkey AI ecosystem — a collection of intelligent assistants, modular tools, and memory-aware agents designed to help users think, plan, and build.

---

## 📁 Project Structure

donkey_workspace/
├── backend/ # Django backend with assistants, memory, projects, etc.
├── frontend/ # React + Vite frontend with Bootstrap styling
├── AGENTS.md # Codex agent guide and dev protocols
├── README.md # You’re here!
└── .gitignore

---

## 🧠 Assistant Architecture

Assistants are the core of this system. Each assistant can:

- Chat with users
- Create or link to Projects and MemoryEntries
- Assign an active project and view scoped memories
- Spawn sub-assistants or agents for complex tasks
- Trigger reflections or prompt evaluations

They are powered by:

- `prompts/` – reusable system prompt templates
- `memory/` – memory chains, entries, reflections
- `projects/` – tasks, milestones, project plans
- `mcp_core/` – orchestration glue + context protocol
- `intel_core/` – document ingestion and chunked search

---

## 🚀 Getting Started

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
