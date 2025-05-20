from django.urls import path
from . import views

from .views import (
    assistants,
    thoughts,
    projects,
    memory,
    prompts,
    sessions,
    delegations,
    delegation,
    signals,
    tasks,
    objectives,
    cache_tools,
    skills,
    messages,

)

urlpatterns = [
    # Basics
    path("reflection/", assistants.reflect_on_assistant),
    path("create_from_thought/", assistants.create_assistant_from_thought),
    path("thoughts/reflect-on-assistant/", assistants.reflect_on_assistant),
    path("primary/", assistants.primary_assistant_view, name="primary-assistant"),
    path(
        "primary/reflect-now/",
        assistants.primary_reflect_now,
        name="primary-reflect-now",
    ),
    path(
        "primary/spawn-agent/",
        assistants.primary_spawn_agent,
        name="primary-spawn-agent",
    ),
    path(
        "primary/delegations/",
        delegations.primary_delegations,
        name="primary-delegations",
    ),
    # path(
    #     "suggest/",
    #     routing.suggest_assistant,
    #     name="assistant-suggest",
    # ),
    path(
        "suggest_delegate/",
        delegation.suggest_delegate,
        name="suggest-delegate",
    ),
    # path("suggest/", routing.suggest_assistant, name="assistant-suggest"),
    # path("routing-history/", routing.routing_history, name="routing-history"),
    path("", assistants.assistants_view, name="assistants_view"),
    path("create/", assistants.assistants_view, name="assistants-list-create"),
    # ===== PROJECTS =====
    path(
        "projects/", projects.assistant_projects, name="assistant-projects"
    ),  # GET (list) + POST (create)
    path(
        "projects/<uuid:pk>/",
        projects.assistant_project_detail,
        name="assistant-project-detail",
    ),  # GET, PATCH, DELETE
    path("projects/<uuid:project_id>/tasks/", tasks.assistant_project_tasks),
    path(
        "projects/<uuid:project_id>/assistant-tasks/",
        tasks.assistant_tasks_for_project,
        name="assistant-tasks-for-project",
    ),
    path(
        "projects/<uuid:project_id>/roles/",
        projects.project_roles,
        name="assistant-project-roles",
    ),
    path(
        "projects/<uuid:project_id>/history/",
        projects.project_history,
        name="assistant-project-history",
    ),
    path(
        "projects/<uuid:pk>/regenerate-plan/",
        projects.regenerate_project_plan,
        name="regenerate-project-plan",
    ),
    path(
        "projects/<uuid:pk>/memory-changes/",
        projects.project_memory_changes,
        name="project-memory-changes",
    ),
    path(
        "project-roles/<uuid:role_id>/",
        projects.project_role_detail,
        name="assistant-project-role-detail",
    ),
    path("tasks/<uuid:task_id>/", tasks.assistant_project_task_detail),
    # path(
    #     "projects/<uuid:project_id>/generate_tasks/",
    #     projects.generate_tasks_for_project,
    # ),
    path(
        "projects/tasks/<int:task_id>/",
        tasks.update_or_delete_task,
        name="update_or_delete_task",
    ),
    # ===== OBJECTIVES =====
    path(
        "objectives/<uuid:objective_id>/actions/",
        tasks.assistant_next_actions,
        name="assistant-next-actions",
    ),
    # ===== THOUGHTS =====
    path(
        "projects/<uuid:project_id>/thoughts/",
        thoughts.assistant_project_thoughts,
        name="project-thoughts",
    ),  # GET + POST
    path(
        "<slug:slug>/thoughts/recent/",
        thoughts.get_recent_thoughts,
        name="assistant-recent-thoughts",
    ),
    path("thoughts/reflect-on-doc/", thoughts.reflect_on_doc),
    path("<slug:slug>/session/<uuid:session_id>/", sessions.get_chat_session_messages),
    path(
        "projects/<slug:slug>/thoughts/<int:thought_id>/",
        thoughts.assistant_update_project_thought,
        name="update-project-thought",
    ),  # PATCH
    path(
        "projects/<uuid:project_id>/thoughts/generate/",
        tasks.generate_assistant_project_thought,
        name="generate-assistant-thought",
    ),  # POST
    path(
        "projects/<uuid:project_id>/thoughts/reflect/",
        thoughts.assistant_reflect_on_thoughts,
        name="reflect-on-thoughts",
    ),  # POST
    # ===== REFLECTION INSIGHTS =====
    path(
        "projects/<uuid:project_id>/reflections/",
        memory.assistant_project_reflections,
        name="assistant-reflection-insights",
    ),  # GET + POST
    path(
        "<slug:slug>/reflect-now/",
        thoughts.assistant_reflect_now,
        name="assistant-reflect-now",
    ),
    path(
        "<slug:slug>/dream/",
        thoughts.assistant_dream,
        name="assistant-dream",
    ),
    path(
        "<slug:slug>/reflect_now/",
        memory.reflect_now,
        name="assistant-reflect-now-context",
    ),
    path(
        "<slug:slug>/reflect/chain/",
        memory.reflect_on_memory_chain,
    ),
    path(
        "<slug:slug>/memories/",
        memory.assistant_memories,
        name="assistant-memories",
    ),
    path(
        "<slug:slug>/memory/summary/",
        memory.assistant_memory_summary,
        name="assistant-memory-summary",
    ),
    path(
        "<slug:slug>/memory-to-project/",
        projects.memory_to_project,
        name="memory-to-project",
    ),
    path(
        "<slug:slug>/spawn/",
        delegation.spawn_from_context,
        name="assistant-spawn-from-context",
    ),
    # ===== PROMPTS =====
    path(
        "projects/link_prompt/",
        prompts.link_prompt_to_project,
        name="link-prompt-to-project",
    ),  # POST
    path(
        "projects/<uuid:project_id>/linked_prompts/",
        prompts.linked_prompts,
        name="linked-prompts",
    ),
    path("prompts/bootstrap-from-prompt/", projects.bootstrap_assistant_from_prompt),
    path("assistants/<slug:slug>/projects/", views.projects_for_assistant),
    path("assistants/<slug:slug>/assign_project/", projects.assign_project),
    # GET
    # ===== AI UTILITIES =====
    # path(
    #     "projects/<uuid:pk>/ai_plan/", projects.ai_plan_project, name="ai-plan-project"
    # ),  # POST
    # path(
    #     "projects/generate-mission/",
    #     projects.generate_project_mission,
    #     name="generate-project-mission",
    # ),  # POST
    # ===== MEMORY LINKS & CHAINS =====
    path(
        "projects/link_memory/",
        memory.link_memory_to_project,
        name="link-memory-to-project",
    ),  # POST
    path(
        "projects/<uuid:project_id>/linked_memories/",
        memory.linked_memories,
        name="linked-memories",
    ),  # GET
    path(
        "projects/<uuid:project_id>/memory-chains/",
        memory.assistant_memory_chains,
        name="assistant-memory-chains",
    ),  # GET + POST
    path(
        "memory-chains/<uuid:chain_id>/",
        memory.assistant_memory_chain_detail,
        name="assistant-memory-chain-detail",
    ),
    # ===== MILESTONES =====
    # ===== SIGNAL SOURCES & CATCHES =====
    path("sources/", signals.signal_sources, name="signal-sources"),  # GET + POST
    path("signals/", signals.signal_catches, name="signal-catches"),  # GET
    path(
        "signals/create/", signals.create_signal_catch, name="create-signal-catch"
    ),  # POST
    path("signals/<uuid:pk>/", signals.update_signal_catch, name="update-signal-catch"),
    # Demo Agents
    path("demos/", assistants.demo_assistant, name="demo_assistant"),
    # Sessions
    path("sessions/list/", sessions.list_chat_sessions, name="chat_session_list"),
    path(
        "sessions/detail/<str:session_id>/",
        sessions.chat_session_detail,
        name="chat_session_detail",
    ),
    path(
        "messages/feedback/", thoughts.submit_chat_feedback, name="submit_chat_feedback"
    ),
    path(
        "messages/<uuid:uuid>/update/",
        thoughts.update_message_feedback,
        name="update_message_feedback",
    ),
    path("messages/send/", messages.send_message, name="assistant-message-send"),
    # path("handoff/", handoffs.create_handoff, name="create-handoff"),
    # path("handoff/<uuid:session_id>/", handoffs.list_handoffs, name="list-handoffs"),
    path(
        "messages/inbox/<slug:slug>/",
        messages.inbox,
        name="assistant-message-inbox",
    ),
    path(
        "messages/outbox/<slug:slug>/",
        messages.outbox,
        name="assistant-message-outbox",
    ),
    path("thoughts/<uuid:pk>/feedback/", thoughts.update_reflection_feedback),
    path("thoughts/<uuid:id>/mutate/", thoughts.mutate_thought, name="mutate-thought"),
    path("thoughts/<uuid:id>/", thoughts.assistant_thought_detail),
    # path("delegations/recent/", views.recent_delegation_events),
    # path("delegation_events/recent/", views.recent_delegation_events),
    path(
        "delegation/<uuid:id>/feedback/",
        delegation.delegation_event_feedback,
        name="delegation-event-feedback",
    ),
    path(
        "<slug:slug>/sessions/",
        sessions.sessions_for_assistant,
        name="assistant-sessions",
    ),
    path(
        "<slug:slug>/session-summary/<uuid:session_id>/",
        sessions.session_summary,
        name="assistant-session-summary",
    ),
    path(
        "<slug:slug>/delegations/",
        delegations.delegation_events_for_assistant,
        name="assistant-delegations",
    ),
    path(
        "<slug:slug>/delegation-trace/",
        delegations.delegation_trace,
        name="assistant-delegation-trace",
    ),
    path(
        "<slug:slug>/hierarchical-memory/",
        delegations.hierarchical_memory,
        name="assistant-hierarchical-memory",
    ),
    path(
        "<slug:slug>/evaluate-delegation/",
        delegations.evaluate_delegation,
        name="assistant-evaluate-delegation",
    ),
    path(
        "<slug:slug>/suggest-delegation/",
        delegations.suggest_delegation,
        name="assistant-suggest-delegation",
    ),
    path(
        "<slug:slug>/handoff/",
        delegations.handoff_session,
        name="assistant-handoff",
    ),
    path("<slug:slug>/reflections/recent/", thoughts.get_recent_reflections),
    path(
        "<slug:slug>/reflections/",
        memory.assistant_reflection_logs,
        name="assistant-reflection-logs",
    ),
    path(
        "reflections/<uuid:id>/",
        memory.assistant_reflection_detail,
        name="assistant-reflection-detail",
    ),
    path(
        "reflections/<uuid:id>/thoughts/",
        memory.reflection_thoughts,
        name="assistant-reflection-thoughts",
    ),
    path(
        "<slug:slug>/feedback/",
        thoughts.recent_feedback,
        name="assistant-feedback",
    ),
    path(
        "<slug:slug>/skills/",
        skills.assistant_skills,
        name="assistant-skills",
    ),
    # SLUGS MUST STAY AT THE BOTTOM!
    path(
        "<slug:slug>/chat/", assistants.chat_with_assistant_view, name="assistant-chat"
    ),
    # path("<slug:slug>/memories/", memory.assistant_memories, name="assistant-memories"),
    path(
        "<slug:slug>/thoughts/",
        thoughts.assistant_thoughts_by_slug,
        name="assistant_thoughts_by_slug",
    ),
    path(
        "<slug:slug>/thought-map/",
        thoughts.assistant_thought_map,
        name="assistant-thought-map",
    ),
    path(
        "<slug:slug>/reflect/",
        thoughts.reflect_on_assistant_thoughts,
        name="assistant_reflect_on_thoughts",
    ),
    path(
        "<slug:slug>/self_reflect/",
        assistants.self_reflect,
        name="assistant-self-reflect",
    ),
    path(
        "<slug:slug>/submit-thought/",
        thoughts.submit_assistant_thought,
        name="submit-assistant-thought",
    ),
    # Assistant Objectives
    path(
        "projects/<uuid:project_id>/objectives/",
        objectives.assistant_objectives,
        name="assistant-objectives",
    ),
    path(
        "<slug:slug>/objectives/",
        objectives.objectives_for_assistant,
        name="objectives-for-assistant",
    ),
    path(
        "<slug:slug>/reflect-to-objectives/",
        objectives.reflect_to_objectives,
        name="reflect-to-objectives",
    ),
    path(
        "<slug:slug>/objectives/from-reflection/",
        objectives.objective_from_reflection,
        name="objective-from-reflection",
    ),
    path(
        "<slug:slug>/plan-tasks/<uuid:objective_id>/",
        tasks.plan_tasks_for_objective,
        name="plan-tasks-objective",
    ),
    path(
        "<slug:slug>/tasks/propose/",
        tasks.propose_task,
        name="assistant-propose-task",
    ),
    path(
        "<slug:slug>/flush/",
        thoughts.flush_chat_session_to_log,
        name="flush-chat-session",
    ),
    path(
        "<slug:slug>/flush-reflection-cache/",
        cache_tools.flush_reflection_cache,
        name="flush-reflection-cache",
    ),
    path(
        "<slug:slug>/simulate-memory/",
        memory.simulate_memory,
        name="assistant-simulate-memory",
    ),
    path(
        "<slug:slug>/drift-check/",
        assistants.drift_check,
        name="assistant-drift-check",
    ),
    path("<slug:slug>/", assistants.assistant_detail_view, name="assistant-detail"),
]
