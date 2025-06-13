from django.urls import get_resolver, URLPattern, URLResolver
from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
import inspect
from capabilities.registry import get_capability_for_path
import subprocess
import json
from pathlib import Path
from django.forms.models import model_to_dict


def _walk_patterns(patterns, prefix=""):
    routes = []
    for p in patterns:
        if isinstance(p, URLResolver):
            routes.extend(_walk_patterns(p.url_patterns, prefix + str(p.pattern)))
        elif isinstance(p, URLPattern):
            try:
                callback = p.callback
                route = prefix + str(p.pattern)
                routes.append(
                    {
                        "path": route,
                        "view": callback.__name__,
                        "module": inspect.getmodule(callback).__name__,
                        "name": getattr(p, "name", None),
                        "capability": get_capability_for_path(route),
                    }
                )
            except Exception as e:
                routes.append({"path": prefix + str(p.pattern), "error": str(e)})
    return routes


def get_full_route_map():
    resolver = get_resolver()
    return _walk_patterns(resolver.url_patterns)


class RouteInspector:
    @staticmethod
    def get_routes():
        return get_full_route_map()


@api_view(["GET"])
@never_cache
def full_route_map(request):
    routes = get_full_route_map()
    return Response({"routes": routes})


@api_view(["GET"])
def template_health_summary(request):
    result = subprocess.run(
        ["python", "manage.py", "inspect_template_health", "--include-rag"],
        capture_output=True,
        text=True,
    )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return Response({"error": result.stderr})

    templates = []
    for item in data:
        path = item.get("template_path")
        tracked = (
            subprocess.run(
                ["git", "ls-files", "--error-unmatch", str(path)],
                capture_output=True,
            ).returncode
            == 0
        )
        item["git_tracked"] = tracked
        templates.append(item)

    return Response({"templates": templates})


@api_view(["POST"])
def reload_templates(request):
    from django.template import engines

    for e in engines.all():
        e.engine.template_loaders = None
    return Response({"reloaded": True})


@api_view(["GET"])
def template_detail(request, slug):
    path = Path(slug)
    info = {}
    status_file = Path("logs/template_status.json")
    if status_file.exists():
        all_info = json.loads(status_file.read_text())
        info = all_info.get(str(path), {})
    content = ""
    if path.exists():
        content = path.read_text()
    return Response({"path": str(path), "content": content, "info": info})


@api_view(["GET"])
def template_diff(request, slug):
    path = Path(slug)
    try:
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(path)],
            check=True,
            capture_output=True,
        )
        result = subprocess.run(
            ["git", "diff", str(path)], capture_output=True, text=True
        )
        diff_text = result.stdout
        tracked = True
    except subprocess.CalledProcessError:
        diff_text = ""
        tracked = False
    return Response({"path": str(path), "diff": diff_text, "tracked": tracked})


from api.permissions import AdminOnly


@api_view(["GET"])
@permission_classes([AdminOnly])
def export_assistants(request):
    """Return a JSON dump of all assistants."""
    from assistants.models.assistant import Assistant

    assistants = [model_to_dict(a) for a in Assistant.objects.all()]
    return Response({"assistants": assistants})


@api_view(["GET"])
@permission_classes([AdminOnly])
def export_routes(request):
    """Return a JSON dump of all URL routes with view info."""
    routes = get_full_route_map()
    return Response({"routes": routes})


@api_view(["GET"])
@permission_classes([AdminOnly])
def export_templates(request):
    """Return template health info as raw JSON."""
    result = subprocess.run(
        ["python", "manage.py", "inspect_template_health", "--include-rag"],
        capture_output=True,
        text=True,
    )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return Response({"error": result.stderr})
    return Response({"templates": data})


@api_view(["GET"])
@permission_classes([AdminOnly])
def rag_debug_logs(request):
    """Return recent RAG diagnostic logs."""
    from memory.models import RAGDiagnosticLog
    from memory.serializers import RAGDiagnosticLogSerializer

    qs = RAGDiagnosticLog.objects.all().order_by("-timestamp")
    assistant_slug = request.GET.get("assistant")
    if assistant_slug:
        qs = qs.filter(assistant__slug=assistant_slug)
    logs = qs[:100]
    data = RAGDiagnosticLogSerializer(logs, many=True).data
    return Response({"results": data})


@api_view(["GET"])
@permission_classes([AllowAny])
def auth_debug(request):
    return Response(
        {
            "authenticated": request.user.is_authenticated,
            "user": request.user.username if request.user.is_authenticated else None,
            "session_keys": list(request.session.keys()),
            "cookies": {
                k: request.COOKIES.get(k)
                for k in ["access", "refresh"]
                if k in request.COOKIES
            },
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def assistant_routing_debug(request):
    """Return onboarding status and primary assistant slug."""

    if not request.user.is_authenticated:
        return Response({"onboarding_complete": False, "primary_slug": None})

    return Response(
        {
            "onboarding_complete": bool(
                getattr(request.user, "onboarding_complete", False)
            ),
            "primary_slug": getattr(request.user, "primary_assistant_slug", None),
        }
    )


@api_view(["POST"])
@permission_classes([AdminOnly])
def reset_onboarding(request):
    """Reset onboarding flags for the given user or current user."""
    user_id = request.data.get("user_id") or request.user.id
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    user.onboarding_complete = False
    user.primary_assistant_slug = None
    user.save(update_fields=["onboarding_complete", "primary_assistant_slug"])
    return Response({"status": "reset"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def embedding_debug(request):
    """Return summary stats about embeddings."""
    from intel_core.models import EmbeddingMetadata
    from embeddings.models import Embedding
    from django.db.models import Count
    from django.contrib.contenttypes.models import ContentType
    from memory.models import MemoryEntry
    from intel_core.models import DocumentChunk
    from prompts.models import Prompt

    model_counts = list(
        EmbeddingMetadata.objects.values("model_used")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    ct_memory = ContentType.objects.get_for_model(MemoryEntry)
    ct_chunk = ContentType.objects.get_for_model(DocumentChunk)
    ct_prompt = ContentType.objects.get_for_model(Prompt)
    allowed = {ct_memory.id, ct_chunk.id, ct_prompt.id}

    invalid = 0
    for emb in Embedding.objects.select_related("content_type"):
        ct = emb.content_type
        obj = emb.content_object
        expected = None
        if ct and emb.object_id:
            expected = f"{ct.model}:{emb.object_id}"
        if not ct or ct.id not in allowed or obj is None or emb.content_id != expected:
            invalid += 1

    # Count embeddings grouped by their related memory entry's assistant and
    # context. GenericForeignKey relations can't be traversed directly in a
    # values() query, so we start from MemoryEntry where the GenericRelation
    # resides. This avoids FieldError when attempting to use
    # ``content_object__...`` lookups on Embedding.
    breakdown = list(
        MemoryEntry.objects.filter(embeddings__isnull=False)
        .values("assistant__id", "assistant__slug", "context_id")
        .annotate(count=Count("embeddings__id"))
        .order_by("-count")
    )

    context_stats = []
    assistants_no_docs = []
    retrieval_checks = []
    if request.GET.get("include_rag") == "1":
        from assistants.utils.chunk_retriever import get_relevant_chunks
        from assistants.models import Assistant

        for a in Assistant.objects.all():
            count = 0
            if a.memory_context_id:
                chunks, *_ = get_relevant_chunks(
                    str(a.id),
                    "purpose",
                    memory_context_id=str(a.memory_context_id),
                )
                count = len(chunks)
            if a.documents.count() == 0:
                assistants_no_docs.append(a.slug)
            retrieval_checks.append(
                {
                    "assistant": a.slug,
                    "documents": a.documents.count(),
                    "retrieved": count,
                }
            )
            context_stats.append(
                {
                    "assistant": a.slug,
                    "context_id": (
                        str(a.memory_context_id) if a.memory_context_id else None
                    ),
                    "chunk_count": count,
                }
            )

    return Response(
        {
            "model_counts": model_counts,
            "invalid_links": invalid,
            "assistant_breakdown": breakdown,
            "context_stats": context_stats,
            "assistants_no_docs": assistants_no_docs,
            "retrieval_checks": retrieval_checks,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def embedding_audit(request):
    """Return counts of embedding mismatches and orphans."""
    from django.contrib.contenttypes.models import ContentType
    from django.db.models import Count
    from embeddings.models import Embedding, EmbeddingDebugTag
    from memory.models import MemoryEntry
    from intel_core.models import DocumentChunk
    from prompts.models import Prompt

    ct_memory = ContentType.objects.get_for_model(MemoryEntry)
    ct_chunk = ContentType.objects.get_for_model(DocumentChunk)
    ct_prompt = ContentType.objects.get_for_model(Prompt)
    allowed = {ct_memory.id, ct_chunk.id, ct_prompt.id}

    stats = {}
    for emb in Embedding.objects.select_related("content_type"):
        ct = emb.content_type
        obj = emb.content_object
        if not ct or ct.id not in allowed:
            continue
        model = ct.model
        entry = stats.setdefault(model, {"mismatched": 0, "orphans": 0})
        if obj is None:
            entry["orphans"] += 1
            continue
        expected_ct = ContentType.objects.get_for_model(obj.__class__)
        expected_oid = str(obj.id)
        expected_cid = f"{expected_ct.model}:{obj.id}"
        if (
            emb.content_type_id != expected_ct.id
            or str(emb.object_id) != expected_oid
            or emb.content_id != expected_cid
        ):
            entry["mismatched"] += 1

    recent = list(
        EmbeddingDebugTag.objects.filter(reason="orphaned-object")
        .order_by("-created_at")
        .values("embedding_id", "reason", "created_at")[:20]
    )

    pending = list(
        EmbeddingDebugTag.objects.filter(status="pending")
        .select_related("embedding")
        .values(
            "id",
            "embedding_id",
            "reason",
            "status",
            "repaired_at",
            "created_at",
            "embedding__content_id",
        )[:100]
    )

    context_audit = list(
        MemoryEntry.objects.filter(embeddings__debug_tags__status="pending")
        .values(
            "assistant__slug",
            "assistant__name",
            "context_id",
        )
        .annotate(count=Count("embeddings__debug_tags"))
        .order_by("-count")
    )

    return Response(
        {
            "results": list(stats.items()),
            "recent_orphans": recent,
            "pending": pending,
            "context_audit": context_audit,
        }
    )


@api_view(["PATCH"])
@permission_classes([AdminOnly])
def embedding_audit_fix(request, tag_id):
    """Attempt to repair a flagged embedding."""
    from django.shortcuts import get_object_or_404
    from django.utils import timezone
    from embeddings.models import EmbeddingDebugTag
    from embeddings.utils.link_repair import repair_embedding_link

    action = request.data.get("action", "fix")
    tag = get_object_or_404(EmbeddingDebugTag, id=tag_id)
    if action == "ignore":
        tag.status = "ignored"
        tag.save(update_fields=["status"])
        return Response({"status": "ignored"})

    changed = repair_embedding_link(tag.embedding)
    if changed:
        tag.status = "repaired"
        tag.repaired_at = timezone.now()
    else:
        tag.status = "ignored"
    tag.save(update_fields=["status", "repaired_at"])
    return Response({"status": tag.status})
