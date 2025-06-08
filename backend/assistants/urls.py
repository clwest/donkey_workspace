from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from assistants.viewsets.assistant_viewset import AssistantViewSet

from .views import (
    assistants,
    thoughts,
    projects,
    memory,
    playback,
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
    switching,
    empathy,
    collaboration,
    reflection,
    knowledge,
    dashboard,
    diagnostics,
    routing,
    handoffs,
    scene,
    recovery,
    repair,
    intelligence,
    training,
    myth,
    reputation,
    conscience,
    autonomy,
    check_in,
    subassistant,
    hints,
    demo,
    interface as interface_views,
    identity,
    onboarding,
    symbolic,
)
from tasks.views.delegate import TaskDelegateView
from assistants.views.badges import (
    BadgeListView,
    AssistantBadgesView,
    AssistantBadgeProgressView,
)
from insights.views.plan import InsightPlanView

from scheduler.views import standup

router = DefaultRouter()
router.register(r"", views.AssistantViewSet, basename="assistant")


urlpatterns = [
    # Basics
    path("reflection/", assistants.reflect_on_assistant),
    path("create_from_thought/", assistants.create_assistant_from_thought),
    path("promote/", training.promote_trained_agent, name="assistant-promote"),
    path("from-documents/", assistants.assistant_from_documents),
    path("from_demo/", assistants.assistant_from_demo),
    path("from_demo/preview/", assistants.assistant_from_demo_preview),
    path("demo_boost/", demo.replay_demo_boost, name="assistant-demo-boost"),
    path("thoughts/reflect-on-assistant/", assistants.reflect_on_assistant),
    path("conscience/", conscience.conscience_profiles),
    path("reflexive-epistemology/", conscience.reflexive_epistemology),
    path("decision-frameworks/", conscience.decision_frameworks),
    path("codex/voice/", views.codex_voice_command, name="codex-voice"),
    path("rituals/haptic/", views.haptic_ritual, name="haptic-ritual"),
    path("<uuid:id>/identity/", identity.assistant_identity, name="assistant-identity"),
    path(
        "<slug:slug>/identity/",
        identity.assistant_identity_summary,
        name="assistant-identity-summary",
    ),
    path("<uuid:id>/mythpath/", identity.assistant_mythpath, name="assistant-mythpath"),
    path("<uuid:id>/onboard/", onboarding.assistant_onboard, name="assistant-onboard"),
    path(
        "<uuid:assistant_id>/sensory/",
        views.assistant_sensory_profile,
        name="assistant-sensory-profile",
    ),
    path(
        "primary/delegations/",
        delegations.primary_delegations,
        name="primary-delegations",
    ),
    path(
        "primary/create/",
        views.create_primary_assistant_view,
        name="create-primary-assistant",
    ),
    path("suggest/", delegation.suggest_delegate, name="assistant-suggest"),
    path(
        "suggest_delegate/",
        delegation.suggest_delegate,
        name="suggest-delegate",
    ),
    # path("suggest/", routing.suggest_assistant, name="assistant-suggest"),
    path("routing-history/", routing.routing_history, name="routing-history"),
    path("purpose-routing/", autonomy.purpose_routes),
    path("autonomy-models/", autonomy.autonomy_models),
    # ===== PROJECTS =====
    path(
        "projects/", projects.assistant_projects, name="assistant-projects"
    ),  # GET (list) + POST (create)
    path(
        "projects/from-memory/",
        projects.create_project_from_memory,
        name="create_project_from_memory",
    ),
    path(
        "projects/<uuid:pk>/",
        projects.assistant_project_detail,
        name="assistant-project-detail",
    ),  # GET, PATCH, DELETE
    path(
        "project/<uuid:pk>/",
        projects.assistant_project_detail,
        name="assistant-project-detail-alias",
    ),
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
        "projects/<uuid:project_id>/collaboration_logs/",
        collaboration.collaboration_logs_for_project,
        name="project-collaboration-logs",
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
    path(
        "projects/<uuid:project_id>/generate_tasks/",
        projects.generate_tasks_for_project,
        name="generate-project-tasks",
    ),
    path(
        "tasks/<uuid:task_id>/update_status/",
        tasks.update_task_status,
        name="update-task-status",
    ),
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
        "<uuid:id>/dream/initiate/",
        thoughts.assistant_dream_initiate,
        name="assistant-dream-initiate",
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
        "<slug:slug>/memories/prioritized/",
        memory.prioritized_memories,
        name="assistant-prioritized-memories",
    ),
    path(
        "<slug:slug>/memory/summary/",
        memory.assistant_memory_summary,
        name="assistant-memory-summary",
    ),
    path(
        "<slug:slug>/memory-documents/",
        memory.assistant_memory_documents,
        name="assistant-memory-documents",
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
    path(
        "projects/unlink_prompt/<uuid:link_id>/",
        prompts.unlink_prompt_from_project,
        name="unlink-prompt-from-project",
    ),
    path(
        "prompts/recent/",
        prompts.recent_prompts,
        name="recent-prompts",
    ),
    path(
        "<slug:slug>/available_prompts/",
        prompts.available_prompts,
        name="assistant-available-prompts",
    ),
    path(
        "<slug:slug>/update_prompt/",
        prompts.update_assistant_prompt,
        name="assistant-update-prompt",
    ),
    path("prompts/bootstrap-from-prompt/", projects.bootstrap_assistant_from_prompt),
    path("assistants/<slug:slug>/projects/", views.projects_for_assistant),
    path(
        "assistants/<slug:slug>/projects/from-memory/",
        projects.create_project_from_memory,
        name="create-project-from-memory-by-slug",
    ),
    path(
        "<slug:slug>/projects/from-memory/",
        projects.create_project_from_memory,
        name="create-project-from-memory-alias",
    ),
    path("assistants/<slug:slug>/assign_project/", projects.assign_project),
    # GET
    # ===== AI UTILITIES =====
    path(
        "projects/<uuid:pk>/ai_plan/",
        projects.ai_plan_project,
        name="ai-plan-project",
    ),  # POST
    path(
        "projects/generate-mission/",
        projects.generate_project_mission,
        name="generate-project-mission",
    ),  # POST
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
    path("demos/", assistants.get_demo_assistants, name="demo_assistant"),
    path(
        "demo_usage/overview/",
        assistants.demo_usage_overview,
        name="demo_usage_overview",
    ),
    path("demo_feedback/", assistants.demo_feedback, name="demo_feedback"),
    path("demo_recap/<str:session_id>/", assistants.demo_recap, name="demo_recap"),
    path("demo_success/", assistants.demo_success, name="demo_success"),
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
    path("handoff/", handoffs.create_handoff, name="create-handoff"),
    path(
        "handoff/<uuid:session_id>/",
        handoffs.list_handoffs,
        name="list-handoffs",
    ),
    path("handoff-log/", handoffs.create_handoff_log, name="create-handoff-log"),
    path(
        "handoff-log/<slug:slug>/",
        handoffs.list_handoff_logs,
        name="list-handoff-logs",
    ),
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
    path(
        "relay/inbox/<slug:slug>/",
        messages.relay_inbox,
        name="assistant-relay-inbox",
    ),
    path(
        "relay/outbox/<slug:slug>/",
        messages.relay_outbox,
        name="assistant-relay-outbox",
    ),
    # Council
    # <<<<<<< codex/implement-mood-driven-collaboration-styles
    #     path("council/start/", council.start_session, name="council-start"),
    #     path("council/<uuid:id>/", council.session_detail, name="council-detail"),
    #     path(
    #         "council/<uuid:id>/thoughts/", council.session_thoughts, name="council-thoughts"
    #     ),
    #     path("council/<uuid:id>/respond/", council.session_respond, name="council-respond"),
    #     path("council/<uuid:id>/reflect/", council.session_reflect, name="council-reflect"),
    # =======
    #     # path("council/start/", council.start_session, name="council-start"),
    #     # path("council/<uuid:id>/", council.session_detail, name="council-detail"),
    #     # path("council/<uuid:id>/thoughts/", council.session_thoughts, name="council-thoughts"),
    #     # path("council/<uuid:id>/respond/", council.session_respond, name="council-respond"),
    #     # path("council/<uuid:id>/reflect/", council.session_reflect, name="council-reflect"),
    # >>>>>>> main
    path("suggest_switch/", switching.suggest_switch, name="assistant-suggest-switch"),
    path("switch/", switching.switch_session, name="assistant-switch-session"),
    path("thoughts/<uuid:pk>/feedback/", thoughts.update_reflection_feedback),
    path("thoughts/<uuid:id>/mutate/", thoughts.mutate_thought, name="mutate-thought"),
    path("thoughts/<uuid:id>/", thoughts.assistant_thought_detail),
    path(
        "delegation_events/recent/",
        delegation.recent_delegation_events,
        name="recent-delegation-events",
    ),
    path(
        "delegations/recent/",
        delegations.recent_delegations,
        name="recent-delegations",
    ),
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
        "<slug:slug>/subagent_reflect/<uuid:trace_id>/",
        delegations.subagent_reflect,
        name="assistant-subagent-reflect",
    ),
    path(
        "<slug:slug>/subagent_reflect/",
        diagnostics.subagent_reflect,
        name="subagent_reflect",
    ),
    path(
        "delegation/subagent_reflect/<uuid:event_id>/",
        reflection.subagent_reflect_view,
        name="delegation-subagent-reflect",
    ),
    path(
        "<slug:slug>/evaluate-delegation/",
        delegations.evaluate_delegation,
        name="assistant-evaluate-delegation",
    ),
    path(
        "<slug:slug>/evaluate-collaboration/",
        collaboration.evaluate_collaboration,
        name="assistant-evaluate-collaboration",
    ),
    path(
        "<slug:slug>/evaluate-continuity/",
        reflection.evaluate_continuity,
        name="assistant-evaluate-continuity",
    ),
    path(
        "<slug:slug>/summarize_delegations/",
        diagnostics.summarize_delegations,
        name="summarize_delegations",
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
        "<slug:slug>/reflection_review_primer/",
        memory.reflection_review_primer,
        name="assistant-reflection-primer",
    ),
    path(
        "<slug:slug>/reflect_first_use/",
        memory.reflect_first_use,
        name="assistant-reflect-first-use",
    ),
    path(
        "<slug:slug>/reflections/",
        memory.assistant_reflection_logs,
        name="assistant-reflection-logs",
    ),
    path(
        "<slug:slug>/replays/",
        memory.assistant_reflection_replays,
        name="assistant-reflection-replays",
    ),
    path(
        "<slug:slug>/replays/<uuid:id>/diff/",
        memory.reflection_replay_diff,
        name="reflection-replay-diff",
    ),
    path(
        "<slug:slug>/replay_drifted/",
        memory.replay_drifted_reflections,
        name="assistant-replay-drifted",
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
        "reflections/<uuid:id>/replay/",
        memory.replay_reflection,
        name="reflection-replay",
    ),
    path(
        "<slug:slug>/feedback/",
        thoughts.recent_feedback,
        name="assistant-feedback",
    ),
    # path(
    #     "<slug:slug>/skills/",
    #     skills.assistant_skills,
    #     name="assistant-skills",
    # ),
    path(
        "<slug:slug>/empathy/",
        empathy.assistant_empathy,
        name="assistant-empathy",
    ),
    path(
        "<slug:slug>/reflect_empathy/",
        empathy.assistant_reflect_empathy,
        name="assistant-reflect-empathy",
    ),
    path(
        "memory/<uuid:id>/resonance/",
        empathy.memory_resonance,
        name="memory-resonance",
    ),
    # SLUGS MUST STAY AT THE BOTTOM!
    path(
        "<slug:slug>/chat/", assistants.chat_with_assistant_view, name="assistant-chat"
    ),
    # path("<slug:slug>/memories/", memory.assistant_memories, name="assistant-memories"),
    path(
        "<slug:slug>/thoughts/",
        thoughts.AssistantThoughtViewSet.as_view({"get": "list"}),
        name="assistant_thoughts_by_slug",
    ),
    path(
        "<slug:slug>/thought-log/",
        thoughts.AssistantThoughtLogListView.as_view(),
        name="assistant-thought-log",
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
        "<slug:slug>/reflect_on_self/",
        reflection.reflect_on_self,
        name="assistant-reflect-on-self",
    ),
    path(
        "<slug:slug>/self-assess/",
        assistants.self_assess,
        name="assistant-self-assess",
    ),
    path(
        "<slug:slug>/clarify_prompt/",
        assistants.clarify_prompt,
        name="assistant-clarify-prompt",
    ),
    path(
        "<slug:slug>/failure_log/",
        assistants.failure_log,
        name="assistant-failure-log",
    ),
    path(
        "<slug:slug>/rag_debug/",
        assistants.rag_grounding_logs,
        name="assistant-rag-debug",
    ),
    path(
        "<slug:slug>/rag_playback/<uuid:id>/",
        memory.rag_playback_detail,
        name="assistant-rag-playback",
    ),
    path(
        "<slug:slug>/rag_drift_report/",
        assistants.rag_drift_report,
        name="assistant-rag-drift-report",
    ),
    path(
        "<slug:slug>/first_question_stats/",
        assistants.first_question_stats,
        name="assistant-first-question-stats",
    ),
    path(
        "<slug:slug>/drift_suggestions/",
        assistants.drift_suggestions,
        name="assistant-drift-suggestions",
    ),
    path(
        "<slug:slug>/drift_heatmap/",
        assistants.drift_heatmap,
        name="assistant-drift-heatmap",
    ),
    path(
        "<slug:slug>/anchor_health/",
        assistants.anchor_health,
        name="assistant-anchor-health",
    ),
    path(
        "<slug:slug>/glossary_stats/",
        assistants.glossary_stats,
        name="assistant-glossary-stats",
    ),
    path(
        "<slug:slug>/glossary/convergence/",
        assistants.glossary_convergence,
        name="assistant-glossary-convergence",
    ),
    path(
        "<slug:slug>/boost_anchors/",
        assistants.boost_anchors,
        name="assistant-boost-anchors",
    ),
    path(
        "<slug:slug>/suggest_glossary_anchor/",
        assistants.suggest_glossary_anchor,
        name="assistant-suggest-glossary-anchor",
    ),
    path(
        "<slug:slug>/lineage/",
        assistants.assistant_lineage,
        name="assistant-lineage",
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
        "primary/objectives/",
        objectives.primary_objectives,
        name="primary-objectives",
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
        "<slug:slug>/plan-objective/",
        objectives.plan_objective,
        name="plan-objective",
    ),
    path(
        "<slug:slug>/plan-tasks/<uuid:objective_id>/",
        tasks.plan_tasks_for_objective,
        name="plan-tasks-objective",
    ),
    path(
        "<slug:slug>/objectives/<uuid:objective_id>/plan-tasks/",
        tasks.plan_tasks_for_objective,
        name="objective-plan-tasks",
    ),
    path(
        "<slug:slug>/tasks/propose/",
        tasks.propose_task,
        name="assistant-propose-task",
    ),
    path(
        "<slug:slug>/plan-task/",
        tasks.plan_task,
        name="assistant-plan-task",
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
        "<slug:slug>/add_document/",
        assistants.add_document_to_assistant,
        name="assistant-add-document",
    ),
    path(
        "<slug:slug>/review-ingest/<uuid:doc_id>/",
        assistants.review_ingest,
        name="assistant-review-ingest",
    ),
    path(
        "<slug:slug>/drift-check/",
        assistants.drift_check,
        name="assistant-drift-check",
    ),
    path(
        "<slug:slug>/recover/",
        assistants.recover_assistant_view,
        name="assistant-recover",
    ),
    path(
        "<slug:slug>/regenerate_plan/",
        recovery.regenerate_plan,
        name="assistant-regenerate-plan",
    ),
    path(
        "<slug:slug>/reflect_again/",
        repair.reflect_again,
        name="assistant-reflect-again",
    ),
    path(
        "<slug:slug>/repair_documents/",
        repair.repair_documents,
        name="assistant-repair-documents",
    ),
    path(
        "<slug:slug>/plan-from-thread/",
        intelligence.plan_from_thread,
        name="assistant-plan-from-thread",
    ),
    path(
        "<slug:slug>/diff-knowledge/",
        knowledge.diff_knowledge,
        name="assistant-diff-knowledge",
    ),
    path(
        "<slug:slug>/assign-training/",
        training.assign_training,
        name="assistant-assign-training",
    ),
    path(
        "<slug:slug>/evaluate-agent/<uuid:agent_id>/",
        training.evaluate_agent,
        name="assistant-evaluate-agent",
    ),
    path(
        "<slug:slug>/dashboard/",
        dashboard.assistant_dashboard,
        name="assistant-dashboard",
    ),
    path(
        "<slug:slug>/diagnostics/",
        diagnostics.assistant_diagnostics,
        name="assistant-diagnostics",
    ),
    path(
        "<slug:slug>/fix_context/",
        diagnostics.fix_context,
        name="assistant-fix-context",
    ),
    path(
        "<slug:slug>/retag_glossary_chunks/",
        diagnostics.retag_glossary_chunks_view,
        name="assistant-retag-glossary-chunks",
    ),
    path(
        "<slug:slug>/boot_profile/",
        diagnostics.assistant_boot_profile,
        name="assistant-boot-profile",
    ),
    path(
        "<slug:slug>/selftest/",
        diagnostics.assistant_self_test,
        name="assistant-self-test",
    ),
    path(
        "<slug:slug>/rag_self_test/",
        diagnostics.rag_self_test,
        name="assistant-rag-self-test",
    ),
    path(
        "<slug:slug>/collaboration_profile/",
        collaboration.collaboration_profile,
        name="assistant-collaboration-profile",
    ),
    path(
        "<slug:slug>/replay_scene/<uuid:thread_id>/",
        scene.replay_scene_view,
        name="assistant-replay-scene",
    ),
    path(
        "<slug:slug>/chat_with_scene/",
        scene.chat_with_scene,
        name="assistant-chat-with-scene",
    ),
    path(
        "<slug:slug>/myth-layer/",
        myth.assistant_myth_layer,
        name="assistant-myth-layer",
    ),
    path(
        "<slug:slug>/journals/",
        myth.assistant_journals,
        name="assistant-journals",
    ),
    path(
        "<slug:slug>/reputation/",
        reputation.assistant_reputation,
        name="assistant-reputation",
    ),
    path(
        "<slug:slug>/setup_summary/",
        views.AssistantSetupSummaryView.as_view(),
        name="assistant-setup-summary",
    ),
    path(
        "<slug:slug>/summary/",
        assistants.assistant_summary,
        name="assistant-summary",
    ),
    path(
        "<slug:slug>/intro/",
        views.AssistantIntroView.as_view(),
        name="assistant-intro",
    ),
    path(
        "<slug:slug>/trail/",
        views.AssistantTrailRecapView.as_view(),
        name="assistant-trail-recap",
    ),
    path("badges/", BadgeListView.as_view(), name="badge-list"),
    path(
        "<slug:slug>/badges/",
        AssistantBadgesView.as_view(),
        name="assistant-badges",
    ),
    path(
        "<slug:slug>/badge_progress/",
        AssistantBadgeProgressView.as_view(),
        name="assistant-badge-progress",
    ),
    path(
        "<slug:slug>/update_badges/",
        AssistantBadgesView.as_view(),
        name="assistant-update-badges",
    ),
    path(
        "<slug:slug>/hints/",
        hints.assistant_hint_list,
        name="assistant-hints",
    ),
    path(
        "<slug:slug>/demo_tips/",
        demo.demo_tips,
        name="assistant-demo-tips",
    ),
    path(
        "<slug:slug>/hints/<str:hint_id>/dismiss/",
        hints.dismiss_hint,
        name="assistant-hint-dismiss",
    ),
    path(
        "<slug:slug>/tour_progress/",
        hints.tour_progress,
        name="assistant-tour-progress",
    ),
    path(
        "<slug:slug>/tour_started/",
        hints.tour_started,
        name="assistant-tour-started",
    ),
    path(
        "<slug:slug>/clean_memories/",
        assistants.clean_memories,
        name="assistant-clean-memories",
    ),
    path(
        "<slug:slug>/clean_projects/",
        assistants.clean_projects,
        name="assistant-clean-projects",
    ),
    path(
        "<slug:slug>/patch_drifted_reflections/",
        assistants.patch_drifted_reflections,
        name="assistant-patch-reflections",
    ),
    path(
        "<slug:slug>/seed_chat_memory/",
        assistants.seed_chat_memory,
        name="assistant-seed-chat-memory",
    ),
    path(
        "<slug:slug>/reset_demo/",
        assistants.reset_demo_assistant,
        name="assistant-reset-demo",
    ),
    path(
        "<uuid:assistant_id>/check-in/",
        check_in.AssistantCheckInView.as_view(),
        name="assistant-check-in",
    ),
    path(
        "<uuid:assistant_id>/sub-assistants/",
        subassistant.SubAssistantCreateView.as_view(),
        name="create-sub-assistant",
    ),
    path(
        "<uuid:assistant_id>/schedule-standup/",
        standup.StandupScheduleView.as_view(),
        name="schedule-standup",
    ),
    path(
        "<uuid:assistant_id>/collaborate/",
        collaboration.AssistantCollaborationView.as_view(),
        name="assistant-collaborate",
    ),
    path(
        "<uuid:assistant_id>/delegate-task/",
        TaskDelegateView.as_view(),
        name="delegate-task",
    ),
    path(
        "<uuid:assistant_id>/generate-plan/",
        InsightPlanView.as_view(),
        name="generate-plan",
    ),
    path(
        "<uuid:assistant_id>/interface/",
        interface_views.assistant_interface,
        name="assistant-interface",
    ),
    path(
        "new/interface/",
        interface_views.new_assistant_interface,
        name="assistant-new-interface",
    ),
    path("ux/playbooks/", interface_views.ux_playbooks, name="ux-playbooks"),
    path(
        "templates/<str:role>/",
        interface_views.role_template,
        name="role-template",
    ),
    path(
        "interface/tools/",
        interface_views.symbolic_toolkits,
        name="interface-tools",
    ),
    path(
        "ritual/intuition/",
        interface_views.ritual_intuition_panel,
        name="ritual-intuition",
    ),
    path(
        "<uuid:assistant_id>/codex-anchors/",
        symbolic.get_codex_anchors,
        name="assistant-codex-anchors",
    ),
    path(
        "<slug:slug>/codex-anchors/",
        symbolic.CodexAnchorListView.as_view(),
        name="codex-anchors",
    ),
    path(
        "<uuid:assistant_id>/belief-history/",
        symbolic.get_belief_history,
        name="assistant-belief-history",
    ),
    path(
        "<uuid:assistant_id>/belief-forks/",
        symbolic.get_belief_forks,
        name="assistant-belief-forks",
    ),
    path(
        "<slug:slug>/belief-forks/",
        symbolic.BeliefForkListView.as_view(),
        name="belief-forks",
    ),
    # ===== Deployment Planner =====
    path(
        "<uuid:assistant_id>/deploy/",
        views.assistant_deploy,
        name="assistant-deploy",
    ),
    path(
        "<uuid:assistant_id>/tools/",
        views.assistant_toolchain,
        name="assistant-toolchain",
    ),
    path(
        "plan/skills/<uuid:assistant_id>/",
        skills.SkillPlanView.as_view(),
        name="assistant-skill-plan",
    ),
    path(
        "<slug:slug>/run-task/",
        intelligence.run_task,
        name="assistant-run-task",
    ),
    path(
        "<slug:slug>/search-docs/",
        intelligence.search_docs,
        name="assistant-search-docs",
    ),
    # ===== DEBATE ENDPOINTS =====
    # path("debate/start/", debate.start_debate, name="start-debate"),
    # path("debate/<uuid:debate_id>/", debate.get_debate, name="debate-detail"),
    # path(
    #     "debate/<uuid:debate_id>/respond/",
    #     debate.debate_respond,
    #     name="debate-respond",
    # ),
    # path(
    #     "debate/<uuid:debate_id>/consensus/",
    #     debate.debate_consensus,
    #     name="debate-consensus",
    # ),
    path("", include(router.urls)),
]
