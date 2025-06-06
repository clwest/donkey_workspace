from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count

from assistants.serializers import AssistantSerializer
from agents.serializers import AgentSerializer
from intel_core.serializers import DocumentSerializer
from images.serializers import SourceImageSerializer
from .models import UserInteractionSummary
from assistants.models import Assistant
from assistants.utils.onboarding_tracker import get_onboarding_status
from rest_framework_simplejwt.tokens import RefreshToken


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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request):
    assistants = Assistant.objects.filter(created_by=request.user)
    assistant_count = assistants.count()
    glossary_score = assistants.aggregate(avg=Avg("glossary_score"))[
        "avg"
    ] or 0
    onboarding = get_onboarding_status(request.user)
    return Response(
        {
            "username": request.user.username,
            "assistant_count": assistant_count,
            "glossary_score": glossary_score,
            "onboarding_status": onboarding,
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def demo_login(request):
    User = get_user_model()
    user, _ = User.objects.get_or_create(username="demo")
    token = RefreshToken.for_user(user)
    return Response({"access": str(token.access_token), "refresh": str(token)})

