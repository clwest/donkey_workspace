# 🧠 Donkey Workspace

[![CI](https://github.com/example/donkey_workspace/actions/workflows/ci.yml/badge.svg)](https://github.com/example/donkey_workspace/actions/workflows/ci.yml)


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
./scripts/seed_all.sh
```

This script runs all individual seeders and dev documentation scripts sequentially. It also seeds demo sessions, reflection logs, and tour completions so the demo flows work end-to-end.

### Feedback Widget

Use the **Feedback** button in the navbar to report bugs or ideas. Submissions
hit the `/api/feedback/` endpoint and are exported to `GOALS.md` via
`python manage.py export_feedback_goals`.

If you encounter a `ProgrammingError` complaining that `assistants_assistant`
does not exist, ensure you ran `python manage.py makemigrations` before
`python manage.py migrate`. This generates all initial migration files so Django
creates the required tables.

If a migration adds a new model field and you see an error such as
`ProgrammingError: column memory_symbolicmemoryanchor.suggested_label does not exist`,
run `python manage.py makemigrations` again followed by
`python manage.py migrate`. This updates your database schema with the missing
column before executing management commands like `mutate_glossary_anchors`.
If the error mentions `display_tooltip` or `display_location`, you likely pulled
new glossary overlay changes without migrating. Running `python manage.py
migrate` will apply `0008_display_tooltip_location` so the API can load anchors
without crashing.

### Running Tests

Use the helper script to automatically run migrations before executing tests:

```bash
./tests/run_tests.sh
pytest --cov
```

Pass any additional pytest flags after the script. This ensures the database is
fully migrated with the latest models before the test suite runs.

Coverage reports are written to `htmlcov/index.html`. The combined backend and
frontend coverage must remain above **80%**.


### Debugging & Logs

When running the frontend with `npm run dev`, open your browser's developer
console to view network requests and any toast messages. Backend debug logs
appear in the terminal where you started `manage.py runserver`.

## Authentication & Permissions

Use `/api/token/` with your username and password to obtain a JWT:

```bash
curl -X POST -d 'username=me&password=secret' http://localhost:8000/api/token/
```

Store the returned `access` and `refresh` tokens in `localStorage` and attach
`Authorization: Bearer <access>` on API requests. Refresh tokens via
`/api/token/refresh/` when the access token expires.

Write endpoints require authentication and will return `401` when no token is
provided. Assistant-specific endpoints require ownership; unauthorized users
receive `403`.

## Rate Limiting

Anonymous requests are limited to **20 per minute** and authenticated users to
**200 per minute**. Heavy debugging endpoints such as demo replay and RAG logs
use a stricter **10 per minute** throttle. Exceeding these limits returns `429`.

## Security Headers

The backend sets the following headers by default:

- `Content-Security-Policy: default-src 'self'`
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`

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

### Exporting Reflection State

Generate a JSON snapshot of current reflection logs and anchor boosts:

```bash
python manage.py snapshot_reflection_state --assistant=<slug>
```

The file is saved under `backend/exports/` with a timestamped name.


### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Creating an Assistant

Navigate to `/assistants/onboarding` to create your first assistant using the
guided specialty selector. For API examples—including how to personalize a demo—
see [docs/api_overview.md#creating-an-assistant](docs/api_overview.md#creating-an-assistant).

### Docker & Local Dev

Run the full stack with Docker:

```bash
docker-compose up --build
```

Backend logs stream to the console at port 8000 while the frontend is served on
port 5173.

### Docker & Local Dev

Spin up the full stack with Docker:

```bash
docker-compose up --build
```

The API runs at `http://localhost:8000` and the Vite dev server at
`http://localhost:5173`.

### Demo Assistant Flows

Seed demo data and explore recap, overlay, and replay routes:

```bash
cd backend
python manage.py seed_demos
```

Then visit the following URLs (replace `prompt_pal` and session ID as needed):

- `/assistants/prompt_pal/demo_recap/<session_id>/`
- `/assistants/prompt_pal/demo_overlay/`
- `/assistants/prompt_pal/demo_replay/<session_id>/`

These pages link to the assistant's Trust Profile, Trail recap, and Growth panels for a full demo walkthrough.

### Submitting Reflections

After chatting with an assistant you can provide feedback via
`POST /api/assistants/<slug>/reflect/`.
Include `content` and an optional `rating` (1‑5). Recent reflections appear on
the assistant's memory page.

Example API request:

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "My First Assistant", "specialty": "Friendly"}' \
 http://localhost:8000/api/assistants/
```

### Performance Benchmarks

Run the simple benchmark script to measure API latency. Results are saved to
`benchmark_results.json`:

```bash
./scripts/benchmark_endpoints.sh
```
### Monitoring & Alerts

Errors are sent to Sentry when `SENTRY_DSN` is provided. Prometheus metrics are
available at `/metrics/`. Import `docs/grafana_dashboard.json` into Grafana for
basic request and error charts.
See [MAINTENANCE.md](MAINTENANCE.md) for daily health checks and dependency updates.

### CI/CD

GitHub Actions workflows in `.github/workflows` run tests and deploy the Docker
images to the staging environment. See [docs/ci-cd.md](docs/ci-cd.md) for details.
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
- [Demo Slide Deck](docs/slides.md)
- [Release Notes](docs/RELEASE_NOTES.md)
- [Demo Script](docs/DEMO_SCRIPT.md)

### Monitoring & Alerts
Sentry errors are reported using the DSN in `.env`. Prometheus metrics are
exposed at `/metrics/` for Grafana dashboards.
CI and deployment pipelines are documented in [docs/ci-cd.md](docs/ci-cd.md).
See [MAINTENANCE.md](MAINTENANCE.md) for workflow schedules and alert response steps.


- Other domain docs are under `backend/docs/` and `frontend/docs/`.
### Guided Tour\nVisit `/tour` or click **Start Tour** in the Assistant dropdown to see an overlay explaining key panels.

## Internationalization
Translations live under `frontend/src/locales/` and `backend/locale/`. See [docs/i18n.md](docs/i18n.md) for adding new languages.

## Accessibility
The UI targets WCAG 2.1 AA. Automated checks run with `npm test`. Tips and patterns are in [docs/a11y.md](docs/a11y.md).
