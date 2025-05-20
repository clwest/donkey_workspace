from django.urls import path

from .views import ingestion, documents, intelligence

urlpatterns = [
    path("ingestions/", ingestion.unified_ingestion_view, name="intel-load-url"),
    path("documents/", documents.list_documents, name="list_documents"),
    path(
        "documents/<uuid:pk>/", documents.document_detail_view, name="document_detail"
    ),
    path("documents/grouped/", documents.list_grouped_documents, name="list_document_group"),
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
        "intelligence/bootstrap-agent/<uuid:pk>/",
        intelligence.bootstrap_agent_from_docs,
        name="bootstrap_agent_from_docs",
    ),
    path(
        "intelligence/bootstrap-assistant/<uuid:pk>/",
        intelligence.create_bootstrapped_assistant_from_document,
        name="create_bootstrapped_assistant_from_document",
    ),
]
