from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from assistants.serializers import AssistantSerializer
from agents.serializers import AgentSerializer
from intel_core.serializers import DocumentSerializer
from images.serializers import SourceImageSerializer
from .models import UserInteractionSummary


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_assistant(request):
    assistant = getattr(request.user, "personal_assistant", None)
    if not assistant:
        return Response({}, status=404)
    data = AssistantSerializer(assistant).data
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_agents(request):
    assistant = getattr(request.user, "personal_assistant", None)
    if not assistant:
        return Response([])
    agents = assistant.assigned_agents.all()
    data = AgentSerializer(agents, many=True).data
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_documents(request):
    from intel_core.models import Document

    docs = Document.objects.filter(user=request.user)
    data = DocumentSerializer(docs, many=True).data
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_images(request):
    from images.models import SourceImage

    imgs = SourceImage.objects.filter(user=request.user)
    data = SourceImageSerializer(imgs, many=True).data
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_summary(request):
    summary = (
        UserInteractionSummary.objects.filter(user=request.user)
        .order_by("-created_at")
        .first()
    )
    if not summary:
        return Response({})
    data = {
        "message_count": summary.message_count,
        "interaction_summary": summary.interaction_summary,
    }
    return Response(data)

