import warnings

warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views
from .views import accept_mutation

router = DefaultRouter()
router.register("entries", views.MemoryEntryViewSet, basename="memory-entry")
router.register("chains", views.MemoryChainViewSet, basename="memory-chain")
router.register("feedback", views.MemoryFeedbackViewSet, basename="memory-feedback")
from assistants.views import empathy

# Place custom chain routes before the router patterns to avoid
# "list" or "create" being captured as a pk for the ViewSet.
urlpatterns = (
    [
        path("chains/list/", views.list_memory_chains, name="list_memory_chains"),
        path("chains/create/", views.create_memory_chain, name="create_memory_chain"),
    ]
    + router.urls
    + [
        path("save/", views.save_memory, name="save_memory"),
        path("recent/", views.recent_memories, name="recent_memories"),
        path("list/", views.list_memories, name="list_memories"),
        path("reflect/", views.reflect_on_memory, name="reflect-on-memory"),
        path("chains/<uuid:pk>/", views.get_memory_chain, name="get_memory_chain"),
        path(
            "chains/<uuid:chain_id>/summarize/",
            views.summarize_chain_view,
            name="summarize_memory_chain",
        ),
        path(
            "chains/<uuid:chain_id>/flowmap/",
            views.chain_flowmap_view,
            name="memory_chain_flowmap",
        ),
        path(
            "chains/<uuid:chain_id>/cross_project_recall/",
            views.cross_project_recall_view,
            name="memory_chain_cross_recall",
        ),
        path(
            "threads/<uuid:thread_id>/linked_chains/",
            views.linked_chains_view,
            name="memory_thread_linked_chains",
        ),
        path(
            "threads/link_chain/", views.link_chain_to_thread, name="link_chain_thread"
        ),
        path(
            "reflect-on-memories/",
            views.reflect_on_memories,
            name="reflect_on_memories",
        ),
        path("reflection/", views.save_reflection, name="save-reflection"),
        path("upload-voice/", views.upload_voice_clip, name="upload_voice_clip"),
        path(
            "memory/<uuid:memory_id>/feedback/",
            views.list_memory_feedback,
            name="memory-feedback-list",
        ),
        path(
            "memory/feedback/submit/",
            views.submit_memory_feedback,
            name="memory-feedback-submit",
        ),
        path("<uuid:id>/mutate/", views.mutate_memory, name="mutate-memory"),
        path("<uuid:id>/", views.memory_detail, name="memory_detail"),
        path(
            "<uuid:memory_id>/bookmark/", views.bookmark_memory, name="bookmark_memory"
        ),
        path(
            "<uuid:memory_id>/unbookmark/",
            views.unbookmark_memory,
            name="unbookmark_memory",
        ),
        path("bookmarked/", views.bookmarked_memories, name="bookmarked_memories"),
        path("by-tag/<slug:slug>/", views.memories_by_tag),
        path("update-tags/<uuid:id>/", views.update_memory_tags),
        path("replace/<uuid:id>/", views.replace_memory),
        path("vector/", views.vector_memories, name="vector-memories"),
        path("<uuid:id>/resonance/", empathy.memory_resonance, name="memory-resonance"),
        path("memory-braids/", views.memory_braids, name="memory-braids"),
        path(
            "continuity-anchors/", views.continuity_anchors, name="continuity-anchors"
        ),
        path(
            "symbolic-anchors/",
            views.symbolic_anchors,
            name="symbolic-anchors",
        ),
        path(
            "symbolic-anchors/<uuid:pk>/",
            views.update_symbolic_anchor,
            name="symbolic-anchor-detail",
        ),
        path(
            "glossary/anchor/<slug:slug>/",
            views.glossary_anchor_detail,
            name="glossary-anchor-detail",
        ),
        path(
            "glossary/boost_anchor/",
            views.boost_anchor,
            name="glossary-boost-anchor",
        ),
        path(
            "glossary/mutations/",
            views.glossary_mutations,
            name="glossary-mutations",
        ),
        path(
            "glossary/mutations/<uuid:id>/accept",
            views.accept_glossary_mutation,
            name="glossary-mutation-accept",
        ),
        path(
            "glossary/mutations/<uuid:id>/accept/",
            accept_mutation,
            name="accept_mutation",
        ),
        path(
            "glossary/mutations/<uuid:id>/reject",
            views.reject_glossary_mutation,
            name="glossary-mutation-reject",
        ),
        path(
            "symbolic-anchors/<slug:slug>/convergence/",
            views.anchor_convergence_logs,
            name="anchor-convergence-logs",
        ),
        path(
            "symbolic-anchors/convergence/",
            views.assistant_convergence_logs,
            name="assistant-convergence-logs",
        ),
        path("anamnesis/", views.anamnesis, name="anamnesis"),
        path("grove/public/", views.public_memory_grove, name="public-memory-grove"),
        path(
            "diff/<uuid:document_set_id>/",
            views.symbolic_chunk_diff_view,
            name="symbolic-chunk-diff",
        ),
        path(
            "merge-suggestions/",
            views.suggest_memory_merge,
            name="memory-merge-suggest",
        ),
        path(
            "glossary-retries/",
            views.glossary_retry_logs,
            name="glossary-retry-logs",
        ),
    ]
)
