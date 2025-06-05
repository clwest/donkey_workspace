from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
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
from devtools.views import (
    full_route_map,
    template_health_summary,
    reload_templates,
    template_detail,
    template_diff,
    export_assistants,
    export_routes,
    export_templates,
)
from story.views import storyboard_list
from mcp_core.views import threading as thread_views
from mcp_core.views import ontology as ontology_views
from agents.views import agents as agent_views
from agents.views import stabilization as stabilization_views
from capabilities import urls as capability_urls
from assistants.views import onboarding as onboarding_views
from assistants.views import assistants as assistant_views

from assistants.views.diagnostics import run_all_self_tests
from assistants.views import delegation as delegation_views
from assistants.views import delegations as delegations_views
from assistants.views import reflection as reflection_views

from intel_core.views import intelligence as intel_views
import memory.views as memory_views

from tts.urls import router as tts_router
from story.urls import router as story_router
from videos.urls import router as videos_router
from images.urls import router as images_router
from characters.urls import router as characters_router
from storyboard.urls import router as storyboard_router
from simulation.urls import router as simulation_router

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


def subagent_reflect_alias(request, slug, event_id):
    return delegations_views.subagent_reflect(request, slug=slug, trace_id=event_id)


def _collect_routes(patterns, prefix=""):
    """Return a flat list of URL patterns without duplicated prefixes."""
    urls = []
    for p in patterns:
        if hasattr(p, "url_patterns"):
            urls.extend(_collect_routes(p.url_patterns, prefix + str(p.pattern)))
        else:
            path = prefix + str(p.pattern)
            # collapse any accidental double slashes or repeated ``api/`` prefix
            while "//" in path:
                path = path.replace("//", "/")
            path = path.replace("api/api/", "api/")
            urls.append(path)
    return urls


def routes_list(request):
    resolver = get_resolver()
    routes = [
        r for r in _collect_routes(resolver.url_patterns) if str(r).startswith("api")
    ]
    return JsonResponse({"routes": routes})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_router.urls)),
    path("api/routes/", routes_list),
    path("api/dev/routes/fullmap/", full_route_map),
    path("api/dev/routes/fullmap/refresh/", full_route_map),
    path("api/dev/templates/health/", template_health_summary),
    path("api/dev/templates/reload/", reload_templates),
    path("api/dev/templates/<path:slug>/detail/", template_detail),
    path("api/dev/templates/<path:slug>/diff/", template_diff),
    path("api/dev/export/assistants/", export_assistants),
    path("api/dev/export/routes/", export_routes),
    path("api/dev/export/templates/", export_templates),
    path("api/capabilities/", include(capability_urls)),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("onboarding/", onboarding_views.onboarding_create_assistant),
    path(
        "assistants/from-documents/",
        assistant_views.assistant_from_documents,
    ),
    path(
        "assistants/self_tests/run_all/",
        run_all_self_tests,
    ),
    path(
        "assistants/<slug:slug>/summarize_delegations/",
        summarize_delegations,
        name="summarize_delegations",
    ),
    path(
        "assistants/<slug:slug>/reflect_on_self/",
        reflect_on_self,
        name="reflect_on_self",
    ),
    path(
        "assistants/<slug:slug>/subagent_reflect/",
        subagent_reflect,
        name="subagent_reflect",
    ),
    path(
        "api/assistants/self_tests/run_all/",
        run_all_self_tests,
    ),
    path(
        "api/assistants/<slug:slug>/summarize_delegations/",
        delegation_views.summarize_delegations,
    ),
    path(
        "api/assistants/<slug:slug>/reflect_on_self/",
        reflection_views.reflect_on_self,
    ),
    path(
        "api/assistants/<slug:slug>/subagent_reflect/<uuid:event_id>/",
        subagent_reflect_alias,
    ),
    path("api/dj-rest-auth/", include("dj_rest_auth.urls")),
    path("api/dj-rest-auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/tts/", include("tts.urls")),
    path("api/stories/", include("story.urls")),
    path("api/videos/", include("videos.urls")),
    path("api/images/", include("images.urls")),
    path("", include("project.urls")),
    path("api/characters/", include("characters.urls")),
    path("api/mythcasting/", include("mythcasting.urls")),
    path("api/mythos/", include("mythos.urls")),
    path("api/users/", include("accounts.urls")),
    path("api/storyboard/", include("storyboard.urls")),
    # Embedding chunk-match endpoint
    path("api/embeddings/", include("embeddings.urls")),
    # Trainers app endpoints
    # path("api/trainers/", include("trainers.urls")),
    path("api/prompts/", include("prompts.urls")),
    path("api/v1/mcp/", include("mcp_core.urls")),
    path("api/v1/memory/", include("memory.urls")),
    path("api/v1/assistants/", include("assistants.urls")),
    path("api/mcp/", include("mcp_core.urls")),
    path("api/memory/", include("memory.urls")),
    path("api/shared-memory-pools/", include("memory.shared_urls")),
    path("api/assistants/", include("assistants.urls")),
    path("api/agents/", include("agents.urls")),
    path("api/swarm/", include("agents.rewire_urls")),
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
    path("api/persona-fusions/", agent_views.persona_fusions),
    path("api/dialogue-mutations/", agent_views.dialogue_mutations),
    path("api/scene-director/", agent_views.scene_director),
    path("api/storyfields/", agent_views.storyfields),
    path("api/myth-patterns/", agent_views.myth_patterns),
    path("api/intent-harmony/", agent_views.intent_harmony),
    path("api/intel/", include("intel_core.urls")),
    path("api/v1/intel/", include("intel_core.api_urls")),
    path("api/rag/check-source/", intel_views.rag_check_source),
    path("glossary/misses/", intel_views.glossary_misses),
    path("api/glossary/boost_anchor/", memory_views.boost_anchor),
    path("api/signal-artifacts/", agent_views.signal_artifacts),
    path("api/navigation-vectors/", agent_views.navigation_vectors),
    path("api/flux-index/", agent_views.flux_index),
    path("api/deploy/standards/", agent_views.deployment_standards),
    path("api/deploy/narrative/", agent_views.deployment_narratives),
    path("api/deploy/replay/<uuid:vector_id>/", agent_views.deployment_replay),
    path("api/deploy/feedback/", agent_views.deployment_feedback),
    path("api/documents/", include("documents.urls")),
    path("api/tools/", include("tools.urls")),
    path("api/workflows/", include("workflows.urls")),
    path("api/execution-logs/", include("workflows.logs_urls")),
    path("api/metrics/", include("metrics.urls")),
    path("api/learning-loops/", include("learning_loops.urls")),
    path("api/adaptive-loops/", include("learning_loops.config_urls")),
    path("api/simulation/", include("simulation.urls")),
    path("api/resources/", include("resources.urls")),
    path("api/cascade/<str:clause_id>/", ontology_views.cascade_graph),
    path("api/codex/clauses/", ontology_views.codex_clauses),
    path("api/collisions/", ontology_views.swarm_collisions),
    path("api/stabilize/", ontology_views.start_stabilization),
    path(
        "api/stabilize/campaigns/",
        stabilization_views.stabilization_campaigns,
    ),
    path(
        "api/stabilize/<uuid:campaign_id>/finalize/",
        ontology_views.finalize_stabilization_campaign,
    ),
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
