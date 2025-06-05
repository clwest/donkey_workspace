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

Whenever new models are added—such as the `MythchainOutputGenerator`,
`NarrativeArtifactExporter`, `SymbolicPatternBroadcastEngine`,
`CodexClauseFragment`, `FragmentTraceLog`, `RitualDecompositionPlan`,
`DecomposedStepTrace`, `CodexExpansionSuggestion`, and
`SwarmCodificationPattern`—run
`python manage.py makemigrations` followed by `python manage.py migrate`
before running tests or deploying the backend. This ensures all tables are
created and up to date.

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

### Running Tests

Use the helper script to automatically run migrations before executing tests:

```bash
./tests/run_tests.sh
```

Pass any additional pytest flags after the script. This ensures the database is
fully migrated with the latest models before the test suite runs.


### Debugging & Logs

When running the frontend with `npm run dev`, open your browser's developer
console to view network requests and any toast messages. Backend debug logs
appear in the terminal where you started `manage.py runserver`.

### Reflection Caching

Reflection summaries are cached in Redis for faster retrieval. When a cached
summary is served the API response includes `"trace": "[cache]"`. Use the
**Force Refresh** button (or pass `force=true` to the endpoint) to bypass the
cache and generate a new reflection. This explains why results may not change
immediately after repeated requests.

### Document Ingestion Progress

Each PDF upload creates a `DocumentProgress` record tracking chunking. If an
exception interrupts ingestion the record now ends with `status="failed"` and the
error message for diagnostics. Retrieve progress via
`/api/v1/intel/documents/<progress_id>/progress/` to spot stuck uploads.

### Fixing Embedding Status

Occasionally embeddings are generated but the associated `DocumentChunk`
records remain marked as `pending` or `failed`. Run:

```bash
python manage.py fix_embeddings_status
```

to update those chunks to `embedding_status="embedded"` in bulk.


### Frontend

```bash
cd frontend
npm install
npm run dev
```
### API Environment

Prompts are served at `/api/prompts/`. Set `VITE_API_URL` to your backend's `/api` base (e.g., `http://localhost:8000/api`) without a `/v1` suffix unless the backend routes change.


---

## Architecture Overview

The project is split into a Django REST backend and a Vite/React frontend. Core apps like `assistants`, `memory`, `intel_core`, and `projects` interact through REST endpoints documented under `docs/`. The high-level relationships are shown in [`docs/architecture_diagram.md`](docs/architecture_diagram.md).

---

## AGENTS Workflow

Development is guided by [`AGENTS.md`](AGENTS.md). This file tracks phase objectives and outlines how Codex agents collaborate on new features. Read it regularly to stay aligned with the current phase plan.

Additional planning and deep-dive instructions live in `backend/AGENTS.md` and `frontend/AGENTS.md`.

---

## Phase Ω.5.8 Highlights

Phase Ω.5.8 expands the codex with modular tools:

- **Codex Fragmentation Engine** (`/codex/fragment/:clauseId`)
- **Ritual Decomposition Planner** (`/ritual/decompose/:ritualId`)
- **Swarm-Based Codification Strategies** (`/codex/strategy`)

New backend models include `CodexClauseFragment`, `FragmentTraceLog`,
`RitualDecompositionPlan`, `DecomposedStepTrace`, `CodexExpansionSuggestion`,
and `SwarmCodificationPattern`.

---

## Further Reading

- [API & Model Overview](docs/api_overview.md)
- [Phase 6.5 Features](docs/phase_6_5.md)
- [Phase 8.0 Features](docs/phase_8_0.md)
- [Phase 15.3 Features](docs/phase_15_3.md)
- [Phase 15.5 Features](docs/phase_15_5.md)
- [Phase 15.7 Features](docs/phase_15_7.md)

- [Phase 16.0 Features](docs/phase_16_0.md)
- [Phase 16.3 Features](docs/phase_16_3.md)
- [Phase 16.4 Features](docs/phase_16_4.md)
- [Phase X.1 Features](docs/phase_x_1.md)
- [Phase X.3 Features](docs/phase_x_3.md)
- [Phase X.4 Features](docs/phase_x_4.md)
- [Phase Ω.4.3 Features](docs/phase_omega_4_3.md)
- [Phase Ω.4.5 Features](docs/phase_omega_4_5.md)
- [Phase Ω.4.8 Features](docs/phase_omega_4_8.md)
- [Phase Ω.5.4.3 Features](docs/phase_omega_5_4_3.md)
- [Phase Ω.5.5 Features](docs/phase_omega_5_5.md)
- [Phase Ω.5.5.2 Features](docs/phase_omega_5_5_2.md)
- [Phase Ω.5.5.2b Features](docs/phase_omega_5_5_2b.md)
- [Phase Ω.5.7 Features](docs/phase_omega_5_7.md)
- [Phase Ω.5.8 Features](docs/phase_omega_5_8.md)
- [Phase Ω.6.9 Features](docs/phase_omega_6_9.md)


- Other domain docs are under `backend/docs/` and `frontend/docs/`.
