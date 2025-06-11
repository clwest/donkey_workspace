# Patch Plan

The following groups outline how to address the orphaned code.

## Status

### ✅ Resolved
- `assistant_from_documents` is exposed at `/assistants/from-documents/` and is
  used by the document builder UI.
- Prompt template CRUD routes are registered under `/prompts/templates/`.
- `agents.views.rewire.swarm_graph` is available via `/api/swarm/graph/`.

### 🚧 Remaining
- Remove deprecated assistant wrapper views (`assistants_view`,
  `assistant_detail_view`, `primary_*`).
- Remove unused threading helpers (`reflect_on_thread_objective`,
  `refocus_thread`).
- Delete duplicate `utils.belief_cascade.generate_belief_cascade_graph`.
- Clean up caching utilities (`AIResponseCache`, `MemoryCache`).
- Map `delegate_from_objective` under
  `/api/v1/assistants/<slug>/delegate/<objective_id>/`.
- Expose agent endpoints:
  `lore_token_exchange`, `token_market`, `mythflow_insights`,
  `ritual_contracts`, `myth_engines`, `belief_feedback`.
- Confirm `rag_check_source` integration with RAG fallback.
- Integrate or remove `reflect_on_memory` and `run_story_generation` services.
- Schedule Celery tasks (`reflect_on_project_memory`,
  `bootstrap_assistant_from_doc`, `fragment_codex_clause`, `decompose_ritual`,
  `mine_swarm_codification_patterns`, `delegation_health_check`,
  `run_specialization_drift_checks`, `run_drift_check_for_assistant`,
  `evaluate_team_alignment_task`).

## ✂️ Remove
- Deprecated assistant wrappers (`assistants_view`, `assistant_detail_view`, `primary_*`)
- Unused threading helpers (`reflect_on_thread_objective`, `refocus_thread`)
- Duplicate `utils.belief_cascade.generate_belief_cascade_graph`
- Unused caching classes if no integration planned

## 🔗 Wire
- Add CRUD endpoints for prompt templates in `mcp_core`
- Map `delegate_from_objective` under `/api/v1/assistants/<slug>/delegate/<objective_id>/`
- Expose agent endpoints: `lore_token_exchange`, `token_market`, `mythflow_insights`, `ritual_contracts`, `myth_engines`, `belief_feedback`, `swarm_graph`
- Link `assistant_from_documents` to the dashboard creation flow
- Schedule tasks in `codex_tasks.py` and `assistants/tasks.py` via Celery beat

## 🧪 Test
- Write unit tests for newly wired prompt-template endpoints
- Add integration tests covering delegation flow from objectives
- Ensure Celery tasks trigger via signal/beat schedules

