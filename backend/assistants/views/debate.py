from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Max

from assistants.models import (
    Assistant,
    DebateSession,
    DebateThoughtLog,
    DebateSummary,
)
from assistants.serializers import (
    DebateSessionSerializer,
    DebateThoughtLogSerializer,
    DebateSummarySerializer,
)


@api_view(["POST"])
def start_debate(request):
    """Create a new debate session and initial stances."""
    topic = request.data.get("topic")
    memory_id = request.data.get("memory_id")
    project_id = request.data.get("project_id")
    arguments = request.data.get("arguments", [])

    session = DebateSession.objects.create(
        topic=topic or "Debate",
        memory_id=memory_id,
        project_id=project_id,
    )

    for arg in arguments:
        assistant = Assistant.objects.filter(slug=arg.get("assistant")).first()
        if not assistant:
            continue
        DebateThoughtLog.objects.create(
            debate_session=session,
            assistant=assistant,
            round=1,
            position=arg.get("position", "expand"),
            content=arg.get("content", ""),
        )

    serializer = DebateSessionSerializer(session)
    return Response(serializer.data, status=201)


@api_view(["GET"])
def get_debate(request, debate_id):
    session = DebateSession.objects.filter(id=debate_id).first()
    if not session:
        return Response({"error": "Debate not found"}, status=404)
    serializer = DebateSessionSerializer(session)
    return Response(serializer.data)


@api_view(["POST"])
def debate_respond(request, debate_id):
    session = DebateSession.objects.filter(id=debate_id).first()
    if not session:
        return Response({"error": "Debate not found"}, status=404)

    assistant = Assistant.objects.filter(slug=request.data.get("assistant")).first()
    if not assistant:
        return Response({"error": "Assistant not found"}, status=404)

    last_round = (
        session.logs.aggregate(m=Max("round"))[["m"]][0] if session.logs.exists() else 0
    )
    log = DebateThoughtLog.objects.create(
        debate_session=session,
        assistant=assistant,
        round=last_round + 1,
        position=request.data.get("position", "expand"),
        content=request.data.get("content", ""),
    )
    serializer = DebateThoughtLogSerializer(log)
    return Response(serializer.data, status=201)


@api_view(["POST"])
def debate_consensus(request, debate_id):
    session = DebateSession.objects.filter(id=debate_id).first()
    if not session:
        return Response({"error": "Debate not found"}, status=404)

    summarizer = Assistant.objects.filter(slug=request.data.get("assistant")).first()

    latest = {}
    for log in session.logs.order_by("created_at"):
        latest[log.assistant_id] = log.position

    from collections import Counter

    if latest:
        c = Counter(latest.values())
        pos, cnt = c.most_common(1)[0]
        summary_text = f"Majority position: {pos} ({cnt}/{len(latest)})"
    else:
        summary_text = "No positions recorded"

    summary = DebateSummary.objects.create(
        session=session,
        summary=summary_text,
        created_by=summarizer,
    )
    serializer = DebateSummarySerializer(summary)
    return Response(serializer.data, status=201)
