import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from rest_framework.routers import DefaultRouter

from uuid import UUID
from .views import threading, reflection, tags, memories, prompts, narrative_events

router = DefaultRouter()
router.register("threads", threading.ThreadViewSet, basename="thread")
router.register("reflections", reflection.ReflectionViewSet, basename="reflection")

from mcp_core.capabilities.dev_docs import views as dev_docs

urlpatterns = router.urls + [
    path("prompt-usage/", prompts.log_prompt_usage_view, name="log-prompt-usage"),
    path("reflect/", reflection.reflect_on_memories, name="reflect-on-memories"),
    path("reflections/<int:reflection_id>/save/", reflection.save_reflection),
    path("reflections/", reflection.ReflectionListView.as_view()),
    path("reflections/<uuid:reflection_id>/", reflection.reflection_detail),
    path(
        "reflections/<int:pk>/expand/",
        reflection.expand_reflection,
        name="expand-reflection",
    ),
    path(
        "reflection-tags/<str:tag_name>/",
        reflection.reflections_by_tag,
        name="reflections-by-tag",
    ),
    path("top-tags/", tags.top_tags, name="top-tags"),
    path(
        "reflections/recent/", reflection.recent_reflections, name="recent-reflections"
    ),
    path(
        "reflect/custom/",
        reflection.reflect_on_custom_memories,
        name="reflect-on-custom-memories",
    ),
    path(
        "reflections/grouped/",
        reflection.grouped_reflections_view,
        name="grouped-reflections-view",
    ),
    path("memories/", memories.MemoryListView.as_view(), name="list-memories"),
    path(
        "memory/<uuid:id>/relink/",
        memories.relink_memory,
        name="relink-memory",
    ),
    path(
        "agent/<uuid:agent_id>/reflect/",
        reflection.reflect_on_agent_project,
        name="reflect-on-agent",
    ),
    path(
        "agent/projects/<uuid:project_id>/reflections/",
        reflection.project_reflections,
        name="agent-project-reflection",
    ),
    path("threads/overview/", threading.OverviewThreadListView.as_view(), name="threads_overview"),
    path("threads/", threading.NarrativeThreadListView.as_view(), name="narrative_thread_list"),
    path(
        "threads/<uuid:id>/",
        threading.narrative_thread_detail,
        name="narrative_thread_detail",
    ),
    path(
        "threads/<uuid:id>/summary/",
        threading.thread_summary,
        name="thread-summary",
    ),
    path(

        "threads/<uuid:thread_id>/replay/",
        threading.thread_replay,
        name="thread-replay",
    ),
    path(

        "threads/<uuid:id>/merge/",
        threading.merge_thread,
        name="merge-thread",
    ),
    path(
        "threads/<uuid:id>/split/",
        threading.split_thread,
        name="split-thread",
    ),
    path(
        "threads/<uuid:thread_id>/diagnose/",
        threading.diagnose_thread,
        name="diagnose-thread",
    ),
    # path(
    #     "threads/<uuid:thread_id>/diagnostics/",
    #     threading.list_thread_diagnostics,
    #     name="list-thread-diagnostics",
    #     "threads/<uuid:thread_id>/set_objective/",
    #     threading.set_thread_objective,
    #     name="set-thread-objective",
    # ),
    path(
        "threads/<uuid:thread_id>/diagnose/",
        threading.diagnose_thread,
        name="diagnose-thread",
    ),
    path(
        "threads/<uuid:thread_id>/suggest-continuity/",
        threading.suggest_continuity_view,
        name="suggest-thread-continuity",
    ),

    path(
        "threads/<uuid:thread_id>/realign/",
        threading.realign_thread,
        name="realign-thread",
    ),
    path(
        "threads/<uuid:id>/progress/",
        threading.thread_progress,
        name="thread-progress",
    ),


    path(
        "threads/from-memory/", threading.thread_from_memory, name="thread_from_memory"
    ),
    path(
        "threads/auto-thread/", threading.auto_thread_by_tag, name="auto_thread_by_tag"
    ),
    # path("dev_docs/", dev_docs.DevDocListView.as_view(), name="list-dev-docs"),
    path("dev_docs/summarize/", dev_docs.summarize_and_group_devdocs_view),
    path("dev_docs/grouped_history/", dev_docs.grouped_reflection_history),
    path("dev_docs/grouped/<int:pk>/", dev_docs.grouped_reflection_detail),
    path("dev_docs/<int:pk>/reflect/", dev_docs.reflect_on_devdoc_view),
    path("dev_docs/<slug:slug>/", dev_docs.get_dev_doc, name="get-dev-doc"),
    path("dev_docs/<slug:slug>/detail", dev_docs.devdoc_detail),
    path("dev_docs/<slug:slug>/reflection/", dev_docs.devdoc_reflection_by_slug),
    path(
        "narrative_events/<uuid:event_id>/summarize/",
        narrative_events.summarize_event,
        name="summarize-narrative-event",
    ),

    # path("tasks/<task_id>/status/", task_status.TaskStatusView.as_view()),

]
