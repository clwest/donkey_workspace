from django.urls import get_resolver, URLPattern, URLResolver
from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
import inspect
from capabilities.registry import get_capability_for_path
import subprocess
import json
from pathlib import Path
from django.forms.models import model_to_dict
from assistants.models.command_log import AssistantCommandLog
from django.core.management import get_commands, load_command_class
from assistants.serializers import AssistantCommandLogSerializer


TARGET_APPS = {
    "assistants",
    "embeddings",
    "intel_core",
    "mcp_core",
    "memory",
    "project",
    "prompts",
    "tools",
}


def _get_available_commands():
    cmds = get_commands()
    results = [
        {"name": name, "app": app}
        for name, app in cmds.items()
        if any(app.startswith(t) for t in TARGET_APPS)
    ]
    return sorted(results, key=lambda c: c["name"])


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


def _categorize_command(name):
    lower = name.lower()
    if any(k in lower for k in ["embed", "embedding"]):
        return "embedding"
    if any(k in lower for k in ["repair", "fix"]):
        return "repair"
    if "reflect" in lower:
        return "reflection"
    if "rag" in lower:
        return "rag"
    if "sync" in lower:
        return "sync"
    if "tool" in lower:
        return "tools"
    return "misc"


def list_cli_commands():
    allowed_apps = {
        "assistants",
        "embeddings",
        "intel_core",
        "mcp_core",
        "memory",
        "project",
        "prompts",
        "tools",
    }
    results = []
    for name, app in get_commands().items():
        app_label = app.split(".")[-2] if ".management" in app else app
        if app_label not in allowed_apps:
            continue
        try:
            cmd_class = load_command_class(app, name)
            cmd = cmd_class()
            parser = cmd.create_parser("manage.py", name)
            flags = []
            args = []
            for action in parser._actions:
                if action.option_strings:
                    flags.extend(action.option_strings)
                elif action.dest != "args":
                    args.append(action.dest)
            results.append(
                {
                    "name": name,
                    "help": getattr(cmd, "help", ""),
                    "flags": flags,
                    "args": args,
                    "category": _categorize_command(name),
                    "app": app_label,
                }
            )
        except Exception:
            continue
    return results


class RouteInspector:
    @staticmethod
    def get_routes():
        return get_full_route_map()


@api_view(["GET"])
@never_cache
@permission_classes([IsAuthenticated])
def full_route_map(request):
    routes = get_full_route_map()
    return Response({"routes": routes})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def reload_templates(request):
    from django.template import engines

    for e in engines.all():
        e.engine.template_loaders = None
    return Response({"reloaded": True})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
@permission_classes([AdminOnly])
def cli_command_list(request):
    """Return available management commands"""
    commands = list_cli_commands()
    return Response({"results": commands})


@api_view(["POST"])
@permission_classes([AdminOnly])
def run_cli_command(request):
    """Execute a management command asynchronously."""
    command = request.data.get("command")
    flags = request.data.get("flags", "")
    assistant = request.data.get("assistant")
    flag_list = [f for f in flags.split() if f]

    from utils.resolvers import resolve_or_error
    from django.core.exceptions import ObjectDoesNotExist

    log_assistant = None
    if assistant:
        try:
            log_assistant = resolve_or_error(assistant, Assistant)
        except ObjectDoesNotExist:
            log_assistant = None

    log = AssistantCommandLog.objects.create(
        command=command,
        flags=flags,
        created_by=request.user if request.user.is_authenticated else None,
        assistant=log_assistant,
    )
    from .tasks import run_cli_command_task

    run_cli_command_task.delay(log.id, command, flag_list, assistant)
    return Response({"log_id": log.id})


@api_view(["GET"])
@permission_classes([AdminOnly])
def command_log_detail(request, log_id):
    log = get_object_or_404(AssistantCommandLog, id=log_id)
    data = AssistantCommandLogSerializer(log).data
    return Response(data)


@api_view(["GET"])
@permission_classes([AdminOnly])
def command_log_list(request):
    assistant = request.GET.get("assistant")
    logs = AssistantCommandLog.objects.all()
    if assistant:
        logs = logs.filter(assistant__slug=assistant)
    logs = logs.order_by("-created_at")[:50]
    data = AssistantCommandLogSerializer(logs, many=True).data
    return Response({"results": data})


@api_view(["GET"])
@permission_classes([AdminOnly])
def cli_command_summary(request):
    """Return basic list of commands grouped by app."""
    return Response({"results": _get_available_commands()})


@api_view(["GET"])
@permission_classes([AdminOnly])
def assistant_rag_tests(request, slug):
    logs = AssistantCommandLog.objects.filter(
        assistant__slug=slug, command__startswith="run_rag_tests"
    ).order_by("-created_at")
    data = AssistantCommandLogSerializer(logs, many=True).data
    file_used = "rag_tests.json"
    return Response({"file": file_used, "logs": data})


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
    from django.db.models import Count, F, Q
    from assistants.models import Assistant
    from django.contrib.contenttypes.models import ContentType
    from memory.models import MemoryEntry
    from intel_core.models import DocumentChunk, Document
    from prompts.models import Prompt
    from mcp_core.models import DevDoc
    from assistants.utils.resolve import resolve_assistant

    from assistants.models import AssistantReflectionLog, AssistantThoughtLog
    from embeddings.utils.link_repair import embedding_link_matches

    model_counts = list(
        EmbeddingMetadata.objects.values("model_used")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    zero_score_chunks = DocumentChunk.objects.filter(score__lte=0.0).count()

    ct_memory = ContentType.objects.get_for_model(MemoryEntry)
    ct_chunk = ContentType.objects.get_for_model(DocumentChunk)
    ct_prompt = ContentType.objects.get_for_model(Prompt)
    ct_document = ContentType.objects.get_for_model(Document)
    ct_reflection = ContentType.objects.get_for_model(AssistantReflectionLog)
    ct_thought = ContentType.objects.get_for_model(AssistantThoughtLog)
    ct_devdoc = ContentType.objects.get_for_model(DevDoc)

    allowed = {
        ct_memory.id,
        ct_chunk.id,
        ct_prompt.id,
        ct_document.id,
        ct_reflection.id,
        ct_thought.id,
        ct_devdoc.id,
    }

    invalid = 0

    missing_meta_count = Embedding.objects.filter(
        Q(session_id__isnull=True) | Q(source_type__isnull=True)
    ).count()

    orphaned_embeddings = []

    for emb in Embedding.objects.select_related("content_type"):

        ct = emb.content_type
        if not ct or ct.id not in allowed:
            continue
        obj = emb.content_object

        if obj is None:
            invalid += 1
            orphaned_embeddings.append(
                {
                    "embedding_id": emb.id,
                    "expected": emb.content_id,
                    "reason": "missing object",
                }
            )
            continue
        expected_ct = ContentType.objects.get_for_model(obj.__class__)
        expected_cid = f"{expected_ct.model}:{obj.id}"
        expected_oid = str(obj.id)
        if (
            emb.content_type_id != expected_ct.id
            or str(emb.object_id) != expected_oid
            or emb.content_id != expected_cid
        ):

            invalid += 1
            orphaned_embeddings.append(
                {
                    "embedding_id": emb.id,
                    "expected": expected_cid,
                    "actual": emb.content_id,
                    "reason": "mismatched link",
                }
            )

    # Count embeddings grouped by their related memory entry's assistant and
    # context. GenericForeignKey relations can't be traversed directly in a
    # values() query, so we start from MemoryEntry where the GenericRelation
    # resides. This avoids FieldError when attempting to use
    # ``content_object__...`` lookups on Embedding.
    assistant_param = request.GET.get("assistant")
    assistant_obj = resolve_assistant(assistant_param) if assistant_param else None

    entries_qs = MemoryEntry.objects.filter(embeddings__isnull=False)
    if assistant_obj:
        entries_qs = entries_qs.filter(assistant=assistant_obj)
    breakdown = list(
        entries_qs.values("assistant__id", "assistant__slug", "context_id")
        .annotate(count=Count("embeddings__id"))
        .order_by("-count")
    )

    context_stats = []
    duplicate_slugs = list(
        Assistant.objects.values("slug")
        .annotate(c=Count("id"))
        .filter(c__gt=1)
        .values_list("slug", flat=True)
    )
    assistants_no_docs = []
    retrieval_checks = []
    repair_qs = MemoryEntry.objects.filter(
        embeddings__debug_tags__repair_status="pending"
    )
    if assistant_obj:
        repair_qs = repair_qs.filter(assistant=assistant_obj)
    repairable_contexts = list(
        repair_qs.annotate(
            assistant_slug=F("assistant__slug"),
            status=F("embeddings__debug_tags__repair_status"),
        )
        .values("assistant_slug", "context_id", "status")
        .annotate(count=Count("embeddings__debug_tags__id"))
        .order_by("-count")
    )
    if request.GET.get("include_rag") == "1":
        from assistants.utils.chunk_retriever import get_relevant_chunks

        assistants_qs = (
            Assistant.objects.filter(id=assistant_obj.id)
            if assistant_obj
            else Assistant.objects.all()
        )

        for a in assistants_qs:
            count = 0
            if a.memory_context_id:
                chunks, *_ = get_relevant_chunks(
                    str(a.id),
                    "purpose",
                    memory_context_id=str(a.memory_context_id),
                )
                count = len(chunks)

            all_docs = (
                a.documents.count()
                + a.assigned_documents.count()
                + DevDoc.objects.filter(linked_assistants=a).count()
            )
            if all_docs == 0:

                assistants_no_docs.append(a.slug)

            retrieval_checks.append(
                {
                    "assistant": a.slug,
                    "documents": all_docs,
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

    assistants_no_docs = sorted(set(assistants_no_docs))
    return Response(
        {
            "model_counts": model_counts,
            "invalid_links": invalid,
            "missing_metadata_count": missing_meta_count,
            "zero_score_chunks": zero_score_chunks,
            "assistant_breakdown": breakdown,
            "context_stats": context_stats,
            "assistants_no_docs": assistants_no_docs,
            "retrieval_checks": retrieval_checks,
            "repairable_contexts": repairable_contexts,
            "duplicate_slugs": duplicate_slugs,
            "orphaned_embeddings": orphaned_embeddings,
            "orphan_embeddings_count": len(orphaned_embeddings),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def embedding_audit(request):
    """Return counts of embedding mismatches and orphans."""
    from django.contrib.contenttypes.models import ContentType
    from django.db.models import Count, F
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
        EmbeddingDebugTag.objects.filter(repair_status="pending")
        .select_related("embedding", "embedding__content_type")
        .values(
            "id",
            "embedding_id",
            "reason",
            "repair_status",
            "repair_attempts",
            "last_attempt_at",
            "repaired_at",
            "notes",
            "created_at",
            "embedding__content_id",
            "embedding__content_type__model",
        )[:100]
    )

    # GenericForeignKey relations cannot be traversed in ORM filters reliably
    # across Django versions. Instead, we aggregate counts starting from
    # `MemoryEntry`, which exposes a `GenericRelation` to embeddings.
    context_audit = list(
        MemoryEntry.objects.filter(embeddings__debug_tags__isnull=False)
        .annotate(
            assistant_slug=F("assistant__slug"),
            assistant_name=F("assistant__name"),
            status=F("embeddings__debug_tags__repair_status"),
        )
        .values("assistant_slug", "assistant_name", "context_id", "status")
        .annotate(count=Count("embeddings__debug_tags__id"))
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
    from embeddings.models import Embedding, EmbeddingDebugTag
    from embeddings.utils.link_repair import (
        repair_embedding_link,
        embedding_link_matches,
    )

    action = request.data.get("action", "fix")
    tag = get_object_or_404(EmbeddingDebugTag, id=tag_id)
    if action == "ignore":
        tag.repair_status = "ignored"
        tag.save(update_fields=["repair_status"])
        return Response({"status": "ignored"})

    changed = repair_embedding_link(tag.embedding)
    tag.repair_attempts += 1
    tag.last_attempt_at = timezone.now()
    if embedding_link_matches(tag.embedding):
        tag.repair_status = "repaired"
        tag.repaired_at = timezone.now()
    else:
        tag.repair_status = "failed" if changed else "skipped"
    tag.save(
        update_fields=[
            "repair_status",
            "repair_attempts",
            "last_attempt_at",
            "repaired_at",
        ]
    )
    return Response({"status": tag.repair_status})


@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def repair_context_embeddings(request, context_id):
    """Repair all flagged embeddings for a memory context."""
    from django.utils import timezone
    from embeddings.models import EmbeddingDebugTag
    from embeddings.utils.link_repair import (
        repair_embedding_link,
        embedding_link_matches,
    )
    from django.db.models import CharField
    from django.db.models.functions import Cast

    from django.contrib.contenttypes.models import ContentType
    from memory.models import MemoryEntry

    mem_ct = ContentType.objects.get_for_model(MemoryEntry)
    embedding_ids = (
        Embedding.objects.filter(content_type_id=mem_ct.id)
        .filter(
            object_id__in=MemoryEntry.objects.filter(context_id=context_id)
            .annotate(id_str=Cast("id", output_field=CharField()))
            .values("id_str")
        )
        .values_list("id", flat=True)
    )
    tags = list(
        EmbeddingDebugTag.objects.filter(
            embedding_id__in=embedding_ids, repair_status="pending"
        ).select_related("embedding")
    )
    for tag in tags:
        repair_embedding_link(tag.embedding)
        tag.repair_attempts += 1
        tag.last_attempt_at = timezone.now()
        if embedding_link_matches(tag.embedding):
            tag.repair_status = "repaired"
            tag.repaired_at = timezone.now()
        else:
            tag.repair_status = "failed"
        tag.notes = "Patched via UI repair action"
        tag.save(
            update_fields=[
                "repair_status",
                "repair_attempts",
                "last_attempt_at",
                "repaired_at",
                "notes",
            ]
        )

    return Response({"status": "repaired", "count": len(tags)})


@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def ignore_context_embeddings(request, context_id):
    """Mark all pending mismatches for this context as ignored."""
    from django.contrib.contenttypes.models import ContentType
    from memory.models import MemoryEntry
    from embeddings.models import Embedding, EmbeddingDebugTag

    from django.db.models import CharField
    from django.db.models.functions import Cast

    mem_ct = ContentType.objects.get_for_model(MemoryEntry)
    embedding_ids = (
        Embedding.objects.filter(content_type_id=mem_ct.id)
        .filter(
            object_id__in=MemoryEntry.objects.filter(context_id=context_id)
            .annotate(id_str=Cast("id", output_field=CharField()))
            .values("id_str")
        )
        .values_list("id", flat=True)
    )
    updated = EmbeddingDebugTag.objects.filter(
        embedding_id__in=embedding_ids,
        repair_status="pending",
    ).update(repair_status="ignored", notes="Manually ignored from UI")
    return Response({"status": "ignored", "count": updated})


@api_view(["POST"])
@permission_classes([AdminOnly])
def repair_low_score_embeddings(request):
    """Reembed chunks with very low quality scores."""
    from intel_core.models import DocumentChunk
    from embeddings.tasks import embed_and_store

    threshold = float(request.data.get("threshold", 0.1))
    chunks = DocumentChunk.objects.filter(score__lte=threshold)
    count = 0
    for ch in chunks.select_related("embedding"):
        if ch.embedding:
            ch.embedding.is_deleted = True
            ch.embedding.save(update_fields=["is_deleted"])
            ch.embedding = None
        ch.embedding_status = "pending"
        ch.force_embed = True
        ch.save(update_fields=["embedding", "embedding_status", "force_embed"])
        embed_and_store.delay(str(ch.id))
        count += 1
    return Response({"reembedded": count})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def embedding_drift_log(request):
    """Return historical embedding drift logs."""
    from embeddings.models import EmbeddingDriftLog

    logs = list(
        EmbeddingDriftLog.objects.order_by("-timestamp")[:100].values(
            "timestamp",
            "model_name",
            "mismatched_count",
            "orphaned_count",
            "repaired_count",
        )
    )
    return Response({"logs": logs})
