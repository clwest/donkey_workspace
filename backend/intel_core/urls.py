import warnings

warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path

from .views import ingestion, documents, intelligence, debug, chunks

urlpatterns = [
    path("ingestions/", ingestion.unified_ingestion_view, name="intel-load-url"),
    path("ingest/", ingestion.unified_ingestion_view, name="intel-ingest"),
    path("documents/", documents.list_documents, name="list_documents"),
    path(
        "documents/<uuid:pk>/", documents.document_detail_view, name="document_detail"
    ),
    path(
        "documents/grouped/",
        documents.list_grouped_documents,
        name="list_document_group",
    ),
    path(
        "documents/<uuid:pk>/favorite/",
        documents.toggle_favorite,
        name="toggle_favorite_document",
    ),
    path(
        "intelligence/summarize/<uuid:pk>/",
        intelligence.summarize_with_context,
        name="summarize_with_context",
    ),
    path(
        "documents/<uuid:pk>/summarize_with_context/",
        intelligence.summarize_document_with_context,
        name="document_summarize_with_context",
    ),
    path(
        "documents/<uuid:pk>/progress/",
        documents.document_progress_view,
        name="document_progress",
    ),
    path(
        "document-sets/",
        documents.create_document_set,
        name="create_document_set",
    ),
    path(
        "document-sets/<uuid:pk>/",
        documents.document_set_detail,
        name="document_set_detail",
    ),
    path(
        "experiments/bootstrap-assistant/<uuid:pk>/",
        intelligence.create_assistant_from_document_set,
        name="bootstrap_assistant_from_set",
    ),
    path(
        "intelligence/bootstrap-agent/<uuid:pk>/",
        intelligence.bootstrap_agent_from_docs,
        name="bootstrap_agent_from_docs",
    ),
    path(
        "experiments/bootstrap-from-doc/<uuid:pk>/",
        intelligence.create_bootstrapped_assistant_from_document,
        name="bootstrap_from_doc_experiment",
    ),
    path(
        "documents/<uuid:doc_id>/chunks/",
        chunks.document_chunks,
        name="document_chunk_list",
    ),
    path("chunk-stats/", chunks.chunk_stats, name="chunk_stats"),
    path("chunk_drift_stats/", chunks.chunk_drift_stats, name="chunk_drift_stats"),
    path("debug/chunks/<uuid:doc_id>/", debug.debug_doc_chunks),
    path("debug/recalc-scores/", debug.recalc_scores),
    path("debug/rag-recall/", debug.rag_recall),
    path("debug/verify-embeddings/", debug.verify_embeddings),
    path("debug/repair-progress/", debug.repair_progress_view, name="repair-progress"),
    path("debug/fix-embeddings/", debug.fix_embeddings, name="fix-embeddings"),
    path(
        "debug/sync-chunk-counts/",
        debug.sync_chunk_counts_view,
        name="sync-chunk-counts",
    ),
    path(
        "reembed_missing_chunks/",
        debug.reembed_missing_chunks_view,
        name="reembed-missing-chunks",
    ),
    path(
        "glossary/boost/term/",
        debug.boost_glossary_term,
        name="boost-glossary-term",
    ),
    path(
        "glossary/suggest/anchor/",
        debug.suggest_glossary_anchor,
        name="suggest-glossary-anchor",
    ),
]
