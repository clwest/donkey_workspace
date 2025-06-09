from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
import uuid
import logging
from assistants.models.demo_usage import DemoSessionLog

logger = logging.getLogger(__name__)


from assistants.models import (
    Assistant,
    DemoUsageLog,
    ChatSession,
    AssistantChatMessage,
    AssistantReflectionLog,
)
from memory.models import (
    MemoryEntry,
    AnchorReinforcementLog,
    ReflectionReplayLog,
)
from django.utils import timezone

from assistants.demo_config import DEMO_TIPS
from assistants.helpers.demo_utils import (
    generate_assistant_from_demo,
    boost_prompt_from_demo,
)


def bump_demo_score(session_id, delta=0, helpful=False):
    try:
        log = DemoUsageLog.objects.get(session_id=session_id)
    except DemoUsageLog.DoesNotExist:
        return
    log.demo_interaction_score += delta
    if helpful:
        log.tips_helpful += 1
    if log.demo_interaction_score >= 15:
        log.likely_to_convert = True
    fields = ["demo_interaction_score", "likely_to_convert"]
    if helpful:
        fields.append("tips_helpful")
    log.save(update_fields=fields)


@api_view(["GET"])
@permission_classes([AllowAny])
def demo_recap(request, session_id):
    """Return recap data for a demo session unless already shown."""
    try:
        session_id = str(uuid.UUID(str(session_id)))
    except Exception:
        return Response({"error": "invalid"}, status=400)
    session = DemoSessionLog.objects.filter(session_id=session_id).first()
    usage = DemoUsageLog.objects.filter(session_id=session_id).first()
    if not session or not usage:
        logger.warning("[DemoRecap] Missing session or usage for %s", session_id)
        return Response({})
    if session.converted_to_real_assistant or usage.recap_shown:
        return Response(status=404)

    usage.recap_shown = True
    usage.save(update_fields=["recap_shown"])
    return Response(
        {
            "demo_slug": session.assistant.demo_slug,
            "messages_sent": session.message_count,
            "tips_helpful": session.tips_helpful,
            "score": session.demo_interaction_score,
            "starter_query": session.starter_query,
            "converted": session.converted_to_real_assistant,
        }
    )


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def demo_tips(request, slug):
    """Return demo walkthrough tips for a demo assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    if not assistant.is_demo:
        return Response({"tips": []})

    return Response({"tips": DEMO_TIPS})


@api_view(["POST"])
@permission_classes([IsAdminUser])
def replay_demo_boost(request):
    """Clone a demo session and run the boost routine."""
    session_id = request.data.get("demo_session_id")
    if not session_id:
        return Response({"error": "demo_session_id required"}, status=400)
    log = get_object_or_404(DemoUsageLog, session_id=session_id)
    from assistants.utils.session_utils import load_session_messages

    transcript = load_session_messages(session_id)
    assistant = generate_assistant_from_demo(
        log.assistant.demo_slug, request.user, transcript
    )
    summary = boost_prompt_from_demo(assistant, transcript)
    return Response({"slug": assistant.slug, "summary": summary})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def demo_leaderboard(request):
    """Return aggregated demo metrics ranked by conversion rate."""
    session_logs = DemoSessionLog.objects.select_related("assistant")
    usage_logs = DemoUsageLog.objects.all()

    data = {}
    for log in session_logs:
        slug = log.assistant.demo_slug or log.assistant.slug
        entry = data.setdefault(
            slug,
            {
                "demo_slug": slug,
                "label": log.assistant.name,
                "total_sessions": 0,
                "conversion_count": 0,
                "_interaction_total": 0,
                "_message_total": 0,
                "_bounce_count": 0,
                "rating_distribution": {str(i): 0 for i in range(1, 6)},
                "latest_session_date": None,
            },
        )
        entry["total_sessions"] += 1
        if log.converted_to_real_assistant:
            entry["conversion_count"] += 1
        entry["_interaction_total"] += log.demo_interaction_score
        entry["_message_total"] += log.message_count
        if log.message_count <= 1:
            entry["_bounce_count"] += 1
        if (
            not entry["latest_session_date"]
            or log.started_at > entry["latest_session_date"]
        ):
            entry["latest_session_date"] = log.started_at

    for log in usage_logs:
        if not log.user_rating:
            continue
        slug = log.demo_slug
        if slug not in data:
            asst = Assistant.objects.filter(demo_slug=slug).first()
            data[slug] = {
                "demo_slug": slug,
                "label": asst.name if asst else slug,
                "total_sessions": 0,
                "conversion_count": 0,
                "_interaction_total": 0,
                "_message_total": 0,
                "_bounce_count": 0,
                "rating_distribution": {str(i): 0 for i in range(1, 6)},
                "latest_session_date": log.created_at,
            }
        dist = data[slug]["rating_distribution"]
        dist[str(log.user_rating)] = dist.get(str(log.user_rating), 0) + 1
        if (
            not data[slug]["latest_session_date"]
            or log.created_at > data[slug]["latest_session_date"]
        ):
            data[slug]["latest_session_date"] = log.created_at

    results = []
    for slug, entry in data.items():
        total = entry["total_sessions"]
        if total:
            entry["avg_interaction_score"] = entry.pop("_interaction_total") / total
            entry["avg_message_count"] = entry.pop("_message_total") / total
            entry["bounce_rate"] = entry.pop("_bounce_count") / total
            entry["conversion_rate"] = entry["conversion_count"] / total
        else:
            entry["avg_interaction_score"] = 0
            entry["avg_message_count"] = 0
            entry["bounce_rate"] = 0
            entry["conversion_rate"] = 0
            entry.pop("_interaction_total")
            entry.pop("_message_total")
            entry.pop("_bounce_count")
        results.append(entry)

    results.sort(
        key=lambda r: (r["conversion_rate"], r["total_sessions"]), reverse=True
    )
    return Response(results)


@api_view(["GET"])
@permission_classes([AllowAny])
def demo_success_view(request):
    """Return recently created assistants cloned from demos."""
    clones = (
        Assistant.objects.filter(is_demo_clone=True, is_active=True)
        .select_related("spawned_by")
        .order_by("-created_at")
    )
    results = []
    for a in clones:
        first_msg = (
            AssistantChatMessage.objects.filter(session__assistant=a)
            .order_by("created_at")
            .first()
        )
        results.append(
            {
                "slug": a.slug,
                "name": a.name,
                "demo_slug": a.spawned_by.demo_slug if a.spawned_by else None,
                "created_at": a.created_at.isoformat(),
                "memory_count": MemoryEntry.objects.filter(assistant=a).count(),
                "first_message_excerpt": first_msg.content[:100] if first_msg else "",
            }
        )
    return Response(results)


@api_view(["GET"])
@permission_classes([AllowAny])
def demo_reflection_overlay(request, slug):
    """Return reflection overlay details for a demo session."""
    session_id = request.query_params.get("session_id")
    if not session_id:
        return Response({"error": "session_id required"}, status=400)

    try:
        session_uuid = str(uuid.UUID(str(session_id)))
    except Exception:
        return Response({"error": "invalid"}, status=400)

    assistant = get_object_or_404(Assistant, slug=slug)
    session = DemoSessionLog.objects.filter(session_id=session_uuid, assistant=assistant).first()
    start = session.started_at if session else None
    end = session.ended_at or timezone.now() if session else timezone.now()

    usage, _ = DemoUsageLog.objects.get_or_create(
        session_id=session_uuid, defaults={"demo_slug": assistant.demo_slug}
    )

    reflection = usage.reflection
    if not reflection:
        qs = AssistantReflectionLog.objects.filter(
            assistant=assistant, demo_reflection=True
        )
        if start:
            qs = qs.filter(created_at__gte=start)
        reflection = qs.order_by("created_at").first()
        if reflection:
            usage.reflection = reflection
            usage.save(update_fields=["reflection"])

    anchors = AnchorReinforcementLog.objects.filter(
        assistant=assistant,
    )
    if start:
        anchors = anchors.filter(created_at__gte=start)
    if end:
        anchors = anchors.filter(created_at__lte=end)
    anchor_data = [
        {"label": a.anchor.label, "slug": a.anchor.slug}
        for a in anchors.select_related("anchor")
    ]

    mems = (
        MemoryEntry.objects.filter(assistant=assistant, session_id=session_uuid)
        .prefetch_related("tags")
    )
    tag_slugs = {t.slug for m in mems for t in m.tags.all()}
    tags = [{"slug": s} for s in sorted(tag_slugs)]

    drifts = ReflectionReplayLog.objects.filter(
        assistant=assistant,
        created_at__gte=start if start else None,
        created_at__lte=end,
    )
    drift_logs = [
        {"id": str(d.id), "reason": d.drift_reason or ""} for d in drifts
    ]

    snippet = reflection.summary[:200] if reflection else ""

    return Response(
        {
            "anchors": anchor_data,
            "tags": tags,
            "drift_logs": drift_logs,
            "reflection_snippet": snippet,
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_demo_session(request):
    """Clear a demo chat session and related logs."""
    session_id = request.data.get("session_id")
    if not session_id:
        return Response({"error": "session_id required"}, status=400)

    full_reset = request.GET.get("full_reset") == "true"
    session = DemoSessionLog.objects.filter(session_id=session_id).first()
    assistant = session.assistant if session else None
    DemoSessionLog.objects.filter(session_id=session_id).delete()

    if full_reset:
        DemoUsageLog.objects.filter(session_id=session_id).delete()
        try:
            from assistants.models.demo_feedback import DemoFeedbackLog

            DemoFeedbackLog.objects.filter(session_id=session_id).delete()
        except Exception:
            pass
        try:
            from assistants.models.reflection import AssistantReflectionLog

            if assistant:
                AssistantReflectionLog.objects.filter(
                    assistant=assistant, demo_reflection=True
                ).delete()
        except Exception:
            pass

    if assistant:
        from assistants.helpers.logging_helper import log_trail_marker

        log_trail_marker(assistant, "demo_session_reset")

    if getattr(request.user, "demo_session_id", None):
        request.user.demo_session_id = None
        request.user.save(update_fields=["demo_session_id"])

    return Response({"status": "reset"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def demo_replay_debug(request, slug, session_id):
    """Return RAG frames for a demo session."""
    try:
        session_uuid = str(uuid.UUID(str(session_id)))
    except Exception:
        return Response({"error": "invalid"}, status=400)
    assistant = get_object_or_404(Assistant, slug=slug)
    from assistants.utils.session_utils import load_session_messages
    from assistants.utils.chunk_retriever import get_rag_chunk_debug

    messages = load_session_messages(session_uuid)
    user_msgs = [m.get("content", "") for m in messages if m.get("role") == "user"][:3]
    frames = []
    for text in user_msgs:
        info = get_rag_chunk_debug(str(assistant.id), text)
        hits = [c.get("anchor_slug") for c in info["matched_chunks"] if c.get("anchor_slug")]
        frames.append(
            {
                "query": text,
                "chunks": info["matched_chunks"] + info["fallback_chunks"],
                "glossary_hits": hits,
                "glossary_misses": info.get("glossary_misses", []),
                "anchor_boosts": info.get("glossary_scores", {}),
                "retrieval_score": info.get("retrieval_score", 0.0),
                "fallback": info.get("fallback_triggered", False),
                "reason": info.get("reason"),
            }
        )

    reflection = (
        AssistantReflectionLog.objects.filter(assistant=assistant, demo_reflection=True)
        .order_by("created_at")
        .first()
    )
    reflection_summary = reflection.summary if reflection else ""

    return Response({"session_id": session_uuid, "frames": frames, "reflection_summary": reflection_summary})

