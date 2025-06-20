# Phase Ω.6.0 — Document Task Engine, Assistant Execution Trigger & RAG Capability Activation

Phase Ω.6.0 connects assistants with their linked documents and enables simple task execution backed by retrieval augmented generation. Users can trigger a task directly from an assistant page and search across the assistant's document set.

## Core Components
- **CoreAssistant.run_task()** – executes a natural language task and logs the output.
- **`POST /api/assistants/:slug/run-task/`** – run a task for an assistant.
- **`GET /api/assistants/:slug/search-docs/`** – search documents linked to the assistant or its document set.
- **Run Task Panel** – frontend panel to submit a task and display the result.

## View Routes
- `/assistants/:slug/run-task` – API endpoint and UI page.
- `/assistants/:slug/search-docs` – API endpoint returning simple text matches.

---
Prepares for Phase Ω.6.1 — Assistant Benchmark Lab, Task Scoring Engine & Prompt Chain Audit Tracker
