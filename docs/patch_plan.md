# Patch Plan

The following groups outline how to address the orphaned code.

## ✂️ Remove
- Deprecated assistant wrappers (`assistants_view`, `assistant_detail_view`, `primary_*`)
- Unused threading helpers (`reflect_on_thread_objective`, `refocus_thread`)
- Duplicate `utils.belief_cascade.generate_belief_cascade_graph`
- Unused caching classes if no integration planned

## 🔗 Wire
- Add CRUD endpoints for prompt templates in `mcp_core`
- Map `delegate_from_objective` under `/api/v1/assistants/<slug>/delegate/<objective_id>/`
- Expose agent endpoints: `lore_token_exchange`, `token_market`, `mythflow_insights`, `ritual_contracts`, `myth_engines`, `belief_feedback`, `swarm_graph`
- Link `assistant_from_document_set` to the dashboard creation flow
- Schedule tasks in `codex_tasks.py` and `assistants/tasks.py` via Celery beat

## 🧪 Test
- Write unit tests for newly wired prompt-template endpoints
- Add integration tests covering delegation flow from objectives
- Ensure Celery tasks trigger via signal/beat schedules

