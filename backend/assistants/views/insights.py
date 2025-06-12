from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models import Assistant
from insights.models import AssistantInsightLog
from insights.serializers import AssistantInsightLogSerializer
from assistants.utils.chat_reflection import run_chat_reflection


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reflect_on_chat(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    log = run_chat_reflection(assistant, request.user)
    data = AssistantInsightLogSerializer(log).data if log else {}
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def insight_logs(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    logs = AssistantInsightLog.objects.filter(assistant=assistant).order_by("-created_at")
    return Response(AssistantInsightLogSerializer(logs, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_insight(request, slug, pk):
    insight = get_object_or_404(AssistantInsightLog, pk=pk, assistant__slug=slug)
    if insight.proposed_prompt and not insight.accepted:
        assistant = insight.assistant
        if assistant.system_prompt:
            assistant.system_prompt.content = insight.proposed_prompt
            assistant.system_prompt.save(update_fields=["content"])
        insight.accepted = True
        insight.save(update_fields=["accepted"])
    return Response({"status": "ok"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_insight(request, slug, pk):
    insight = get_object_or_404(AssistantInsightLog, pk=pk, assistant__slug=slug)
    insight.accepted = False
    insight.save(update_fields=["accepted"])
    return Response({"status": "rejected"})
