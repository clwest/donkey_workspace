import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
# embeddings/urls.py

from django.urls import path
from . import views as api_views

urlpatterns = [
    # === Core Embedding Tools ===
    path("embed-text/", api_views.embed_text_api, name="embed-text"),
    path("chunk-text/", api_views.chunk_text_api, name="chunk-text"),
    path("search/", api_views.search_embeddings, name="search-embeddings"),
    path("search-targets/", api_views.list_search_targets, name="search-targets"),
    # === Session Tools ===
    path(
        "session/<str:session_id>/documents/",
        api_views.session_docs_api,
        name="session-docs",
    ),
    path("track-session/", api_views.track_session_api, name="track-session"),
    # === Legacy / Specific Tools ===
    path("similar/", api_views.search_similar_embeddings_api, name="search-similar"),
    path(
        "similar-characters/",
        api_views.search_similar_characters,
        name="search-similar-characters",
    ),
]
