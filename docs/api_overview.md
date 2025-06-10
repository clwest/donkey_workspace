# API Overview

This document lists the key REST endpoints and core models used throughout the project. See [RELEASE_NOTES](RELEASE_NOTES.md) for version history.

## Major Endpoints

| Endpoint | Description |
| --- | --- |
| `/api/assistants/` | CRUD operations for assistants and related actions |
| `/api/memory/` | Memory entries, chains, and reflection logs |
| `/api/projects/` | Project, objective, and task management |
| `/api/intel/` | Document ingestion and chunk search |
| `/api/prompts/` | Prompt templates and mutation tools |
| `/api/agents/` | Agent clusters and orchestration hooks |
| `/api/agents/mythflow-plans/` | Create and coordinate symbolic planning frameworks |
| `/api/agents/directive-memory/` | Manage purpose-linked directive memory nodes |
| `/api/agents/planning-lattices/` | Visualize narrative planning lattices |
| `/api/images/` | Image generation and gallery endpoints |
| `/api/characters/` | Character profiles and similarity search |
| `/api/videos/` | Video ingestion and retrieval |
| `/api/assistants/demo_recap/<session_id>/` | Demo session recap data **(v0.1)** |
| `/api/assistants/<slug>/demo_overlay/` | Reflection overlay details for a demo session (pass `session_id`) **(v0.1)** |
| `/api/assistants/<slug>/demo_replay/<session_id>/` | RAG playback frames for debugging **(v0.1)** |
| `/api/purpose-index/` | Track assistant purpose vectors across timelines |
| `/api/belief-signals/` | View belief transmission and inheritance maps |
| `/api/alignment-market/` | Mythic reputation and symbolic economy |

For a full list of routes run `python manage.py show_urls` in the `backend` directory.

## Core Models

- **Assistant** – defines personality, system prompt, current project, and related documents.
- **MemoryEntry** – individual memory chunks linked to an assistant or project.
- **ProjectTask** – tasks and milestones grouped under projects.
- **Prompt** – reusable system or user prompts used by assistants.
- **Document** – ingested PDFs, URLs, or videos searchable by embeddings.

Refer to the files under `backend/**/models/` for detailed fields and relationships.

## Common Tasks

### Creating an Assistant

```python
from assistants.models import Assistant
from prompts.models import Prompt

prompt = Prompt.objects.first()
assistant = Assistant.objects.create(
    name="HelperBot",
    system_prompt=prompt,
    specialty="research",
)
print(assistant.slug)
```

You can also POST to `/api/assistants/`:

```bash
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "My First Assistant", "specialty": "Friendly"}' \
  http://localhost:8000/api/assistants/
```

### Reflect on a Session

Submit user feedback for an assistant:

```bash
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Great help", "rating": 5}' \
  http://localhost:8000/api/assistants/<slug>/reflect/
```

### Ingesting a Document

```python
from intel_core.ingestion import ingest_document

# `source` can be a file path or URL
entry = ingest_document(source="docs/myfile.pdf", created_by=user)
print(entry.document.title)
```

## Demo & QA

Seed all demo data and run benchmarks:

```bash
./scripts/seed_all.sh
./scripts/benchmark_endpoints.sh
cat backend/benchmark_results.json
```

Use `/api/assistants/<slug>/demo_replay/<session_id>/`,
`/api/assistants/<slug>/reflections/`, and `/api/assistants/<slug>/rag_debug/`
to verify demo flows and RAG debugging.
