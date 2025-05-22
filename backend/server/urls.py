from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from django.urls import get_resolver
from story.views import storyboard_list
from mcp_core.views import threading as thread_views
from agents.views import agents as agent_views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/dj-rest-auth/", include("dj_rest_auth.urls")),
    path("api/dj-rest-auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/tts/", include("tts.urls")),
    path("api/stories/", include("story.urls")),
    path("api/videos/", include("videos.urls")),
    path("api/images/", include("images.urls")),
    path("api/projects/", include("project.urls")),
    path("api/characters/", include("characters.urls")),
    path("api/users/", include("accounts.urls")),
    path("api/storyboard/", include("storyboard.urls")),
    # Embedding chunk-match endpoint
    path("api/embeddings/", include("embeddings.urls")),
    # Trainers app endpoints
    # path("api/trainers/", include("trainers.urls")),
    path("api/prompts/", include("prompts.urls")),
    path("api/mcp/", include("mcp_core.urls")),
    path("api/memory/", include("memory.urls")),
    path("api/shared-memory-pools/", include("memory.shared_urls")),
    path("api/assistants/", include("assistants.urls")),
    path("api/agents/", include("agents.urls")),
    path("api/lore-tokens/", agent_views.lore_tokens),
    path("api/codexes/", agent_views.codexes),
    path("api/symbolic-laws/", agent_views.symbolic_laws),
    path("api/ritual-archives/", agent_views.ritual_archives),
    path("api/polities/", agent_views.polities),
    path("api/elections/", agent_views.elections),
    path("api/legacy-roles/", agent_views.legacy_roles),
    path("api/intel/", include("intel_core.urls")),
    path("api/documents/", include("documents.urls")),
    path("api/tools/", include("tools.urls")),
    # path("api/swarm/snapshot/<str:date>/", agent_views.swarm_snapshot),
    path(
        "api/threads/<uuid:thread_id>/replay/",
        thread_views.thread_replay,
        name="thread-replay",
    ),
    # Schema and Docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
