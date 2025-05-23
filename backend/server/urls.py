from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
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

from tts.urls import router as tts_router
from story.urls import router as story_router
from videos.urls import router as videos_router
from images.urls import router as images_router
from characters.urls import router as characters_router
from storyboard.urls import router as storyboard_router
from simulation.urls import router as simulation_router
from simulation.views import projection as projection_views

api_router = DefaultRouter()


def extend_router(prefix: str, router: DefaultRouter) -> None:
    for url_prefix, viewset, basename in router.registry:
        full_prefix = f"{prefix}/{url_prefix}" if url_prefix else prefix
        api_router.register(full_prefix, viewset, basename)


extend_router("tts", tts_router)
extend_router("stories", story_router)
extend_router("videos", videos_router)
extend_router("images", images_router)
extend_router("characters", characters_router)
extend_router("storyboard", storyboard_router)
extend_router("simulation", simulation_router)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_router.urls)),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/dj-rest-auth/", include("dj_rest_auth.urls")),
    path("api/dj-rest-auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/tts/", include("tts.urls")),
    path("api/stories/", include("story.urls")),
    path("api/videos/", include("videos.urls")),
    path("api/images/", include("images.urls")),
    path("", include("project.urls")),
    path("api/characters/", include("characters.urls")),
    path("api/users/", include("accounts.urls")),
    path("api/storyboard/", include("storyboard.urls")),
    # Embedding chunk-match endpoint
    path("api/embeddings/", include("embeddings.urls")),
    # Trainers app endpoints
    # path("api/trainers/", include("trainers.urls")),
    path("api/prompts/", include("prompts.urls")),
    path("api/v1/mcp/", include("mcp_core.urls")),
    path("api/v1/memory/", include("memory.urls")),
    path("api/mcp/", include("mcp_core.urls")),
    path("api/memory/", include("memory.urls")),
    path("api/shared-memory-pools/", include("memory.shared_urls")),
    path("api/assistants/", include("assistants.urls")),
    path("api/agents/", include("agents.urls")),
    path("api/lore-tokens/", agent_views.lore_tokens),
    path("api/codexes/", agent_views.codexes),
    path("api/agent-codices/", agent_views.agent_codices),
    path("api/symbolic-laws/", agent_views.symbolic_laws),
    path("api/ritual-archives/", agent_views.ritual_archives),
    path("api/polities/", agent_views.polities),
    path("api/elections/", agent_views.elections),
    path("api/legacy-roles/", agent_views.legacy_roles),
    path("api/cosmological-roles/", agent_views.cosmological_roles),
    path("api/myth-weaver/", agent_views.myth_weaver),
    path("api/legacy-vaults/", agent_views.legacy_vaults),
    path("api/resonance-graphs/", agent_views.resonance_graphs),
    path("api/cognitive-balance/", agent_views.cognitive_balance_reports),
    path("api/purpose-migrations/", agent_views.purpose_migrations),

    path("api/afterlife-registry/", agent_views.afterlife_registry),
    path("api/continuity-engine/", agent_views.continuity_engine),
    path("api/migration-gates/", agent_views.migration_gates),


    path("api/storyfields/", agent_views.storyfields),
    path("api/myth-patterns/", agent_views.myth_patterns),
    path("api/intent-harmony/", agent_views.intent_harmony),


    path("api/intel/", include("intel_core.urls")),
    path("api/signal-artifacts/", agent_views.signal_artifacts),
    path("api/navigation-vectors/", agent_views.navigation_vectors),
    path("api/flux-index/", agent_views.flux_index), 
    path("api/documents/", include("documents.urls")),
    path("api/tools/", include("tools.urls")),
    path("api/workflows/", include("workflows.urls")),
    path("api/execution-logs/", include("workflows.logs_urls")),
    path("api/metrics/", include("metrics.urls")),
    path("api/learning-loops/", include("learning_loops.urls")),
    path("api/adaptive-loops/", include("learning_loops.config_urls")),
    path("api/simulation/", include("simulation.urls")),
    path("api/memory-projection/", projection_views.memory_projection_frames),
    path("api/belief-walkthroughs/", projection_views.belief_walkthroughs),
    path("api/dreamframes/", projection_views.dreamframes),
    path("api/resources/", include("resources.urls")),
    path(
        "api/threads/<uuid:thread_id>/replay/",
        thread_views.thread_replay,
        name="thread-replay",
    ),
    path(
        "api/v1/threads/<uuid:thread_id>/replay/",
        thread_views.thread_replay,
        name="thread-replay-v1",
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
