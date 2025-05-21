from django.urls import path

from uuid import UUID
from .views import threading, reflection, tags, memories, prompts, narrative_events
from mcp_core.capabilities.dev_docs import views as dev_docs

urlpatterns = [
    path("prompt-usage/", prompts.log_prompt_usage_view, name="log-prompt-usage"),
    path("reflect/", reflection.reflect_on_memories, name="reflect-on-memories"),
    path("reflections/<int:reflection_id>/save/", reflection.save_reflection),
    path("reflections/", reflection.list_reflections),
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

    path("reflections/grouped/", reflection.grouped_reflections_view, name="grouped-reflections-view"),
    path("memories/", memories.list_memories, name="list-memories"),

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
    path("threads/", threading.narrative_thread_list, name="narrative_thread_list"),
    path(
        "threads/<uuid:id>/",
        threading.narrative_thread_detail,
        name="narrative_thread_detail",
    ),
    path(
# <<<<<<< codex/add-thread-continuity-diagnostics
#         "threads/<uuid:thread_id>/diagnose/",
#         threading.diagnose_thread,
#         name="diagnose-thread",
#     ),
#     path(
#         "threads/<uuid:thread_id>/diagnostics/",
#         threading.list_thread_diagnostics,
#         name="list-thread-diagnostics",
# =======
#         "threads/<uuid:thread_id>/set_objective/",
#         threading.set_thread_objective,
#         name="set-thread-objective",
#     ),
#     path(
#         "threads/<uuid:thread_id>/objective/",
#         threading.get_thread_objective,
#         name="get-thread-objective",
#     ),
#     path(
#         "threads/<uuid:thread_id>/reflect/",
#         threading.reflect_on_thread_objective,
#         name="reflect-thread-objective",
# >>>>>>> main
    ),
    path(
        "threads/from-memory/", threading.thread_from_memory, name="thread_from_memory"
    ),
    path(
        "threads/auto-thread/", threading.auto_thread_by_tag, name="auto_thread_by_tag"
    ),
    path("dev_docs/", dev_docs.list_dev_docs, name="list-dev-docs"),
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
]
