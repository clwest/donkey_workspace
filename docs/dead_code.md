# Dead Code Summary

The following views, services, and tasks appear unused or unmapped. They were detected during the orphaned code scan.

## Views not mapped to URLs
- `mcp_core.views.prompts.create_prompt_template`
- `mcp_core.views.prompts.list_prompt_templates`
- `mcp_core.views.prompts.prompt_template_detail`
- `mcp_core.views.threading.reflect_on_thread_objective`
- `mcp_core.views.threading.refocus_thread`
- `assistants.views.assistants.assistants_view`
- `assistants.views.assistants.assistant_detail_view`
- `assistants.views.assistants.primary_assistant_view`
- `assistants.views.assistants.primary_reflect_now`
- `assistants.views.assistants.primary_spawn_agent`
- `assistants.views.delegation.delegate_from_objective`
- `agents.views.agents.lore_token_exchange`
- `agents.views.agents.token_market`
- `agents.views.agents.mythflow_insights`
- `agents.views.agents.ritual_contracts`
- `agents.views.agents.myth_engines`
- `agents.views.agents.belief_feedback`
- `agents.views.rewire.swarm_graph`

## Unused Service Utilities
- `core.services.memory_service.reflect_on_memory`
- `story.services.story_generator.run_story_generation`
- `utils.belief_cascade.generate_belief_cascade_graph` (duplicate)
- `utils.cache_utils.AIResponseCache`
- `utils.cache_utils.MemoryCache`

## Tasks Never Dispatched
- `tasks.codex_tasks.reflect_on_project_memory`
- `tasks.codex_tasks.bootstrap_assistant_from_doc`
- `tasks.codex_tasks.fragment_codex_clause`
- `tasks.codex_tasks.decompose_ritual`
- `tasks.codex_tasks.mine_swarm_codification_patterns`
- `assistants.tasks.delegation_health_check`
- `assistants.tasks.run_specialization_drift_checks`
- `assistants.tasks.run_drift_check_for_assistant`
- `assistants.tasks.evaluate_team_alignment_task`

