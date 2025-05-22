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
- Initiate debate sessions for multiple assistants and record consensus

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
# Run initial migrations for all apps
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### Seeding All Data

Once your backend is running, you can populate every model and DevDoc dataset in one command:

```bash
bash backend/seed_all.sh
```

This script runs all individual seeders and dev documentation scripts sequentially.

If you encounter a `ProgrammingError` complaining that `assistants_assistant`
does not exist, ensure you ran `python manage.py makemigrations` before
`python manage.py migrate`. This generates all initial migration files so Django
creates the required tables.

### Debugging & Logs

When running the frontend with `npm run dev`, open your browser's developer
console to view network requests and any toast messages. Backend debug logs
appear in the terminal where you started `manage.py runserver`.

