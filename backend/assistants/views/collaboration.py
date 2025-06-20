from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from assistants.models.assistant import Assistant
from assistants.models.thoughts import CollaborationLog, CollaborationThread
from assistants.serializers import (
    CollaborationLogSerializer,
    AssistantCollaborationProfileSerializer,
)
from assistants.helpers.collaboration import evaluate_team_alignment


@api_view(["POST"])
@permission_classes([AllowAny])
def evaluate_collaboration(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    project_id = request.data.get("project_id")
    if not project_id:
        return Response({"error": "project_id required"}, status=400)

    log = evaluate_team_alignment(project_id)
    return Response(
        {
            "log_id": str(log.id) if log else None,
            "style_conflict_detected": bool(log and log.style_conflict_detected),
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def collaboration_logs_for_project(request, id):
    logs = CollaborationLog.objects.filter(project_id=id).order_by("-created_at")
    return Response(CollaborationLogSerializer(logs, many=True).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def collaboration_profile(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    return Response(AssistantCollaborationProfileSerializer(assistant).data)


class AssistantCollaborationView(APIView):
    def post(self, request, assistant_id):
        from utils.resolvers import resolve_or_error
        from django.core.exceptions import ObjectDoesNotExist

        try:
            assistant = resolve_or_error(assistant_id, Assistant)
        except ObjectDoesNotExist:
            return Response({"error": "Assistant not found"}, status=404)
        collaborator_ids = request.data.get("assistant_ids", [])
        initial_messages = request.data.get("messages", [])
        thread = CollaborationThread.objects.create(lead=assistant)
        participants = []
        for ident in collaborator_ids:
            try:
                participants.append(resolve_or_error(ident, Assistant))
            except ObjectDoesNotExist:
                continue
        thread.participants.add(*participants, assistant)
        if initial_messages:
            thread.messages = initial_messages
            thread.save(update_fields=["messages"])
        return Response({"thread_id": str(thread.id)})
