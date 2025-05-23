# API Overview

This document lists the key REST endpoints and core models used throughout the project.

## Major Endpoints

| Endpoint | Description |
| --- | --- |
| `/api/assistants/` | CRUD operations for assistants and related actions |
| `/api/memory/` | Memory entries, chains, and reflection logs |
| `/api/projects/` | Project, objective, and task management |
| `/api/intel/` | Document ingestion and chunk search |
| `/api/prompts/` | Prompt templates and mutation tools |
| `/api/agents/` | Agent clusters and orchestration hooks |
| `/api/images/` | Image generation and gallery endpoints |
| `/api/characters/` | Character profiles and similarity search |
| `/api/videos/` | Video ingestion and retrieval |
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

### Ingesting a Document

```python
from intel_core.ingestion import ingest_document

# `source` can be a file path or URL
entry = ingest_document(source="docs/myfile.pdf", created_by=user)
print(entry.document.title)
```
