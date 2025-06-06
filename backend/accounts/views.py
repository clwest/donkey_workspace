from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from django.utils import timezone

from assistants.serializers import AssistantSerializer
from agents.serializers import AgentSerializer
from intel_core.serializers import DocumentSerializer
from images.serializers import SourceImageSerializer
from .models import UserInteractionSummary
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor
from onboarding.utils import (
    get_onboarding_status,
    get_next_onboarding_step,
    record_step_completion,
)
from onboarding.config import STEPS as ONBOARDING_STEPS
import uuid
from rest_framework_simplejwt.tokens import RefreshToken


@api_view(["GET"])
@permission_classes([AllowAny])
def auth_user(request):
    """Return basic user auth info. Publicly accessible."""
    if request.user.is_authenticated:
        assistants = Assistant.objects.filter(created_by=request.user)
        return Response(
            {
                "is_authenticated": True,
                "username": request.user.username,
                "email": request.user.email,
                "onboarding_complete": get_next_onboarding_step(request.user)
                is None,
                "has_assistants": assistants.exists(),
            }
        )
    return Response({"is_authenticated": False})

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
    next_step = get_next_onboarding_step(request.user)
    taught_anchor_exists = SymbolicMemoryAnchor.objects.filter(
        assistant__created_by=request.user,
        acquisition_stage__in=["acquired", "reinforced"],
    ).exists()
    first_assistant = assistants.order_by("created_at").first()
    data = {
        "username": request.user.username,
        "assistant_count": assistant_count,
        "glossary_score": glossary_score,
        "onboarding_status": onboarding,
        "has_assistants": assistant_count > 0,
        "onboarding_complete": next_step is None,
        "has_taught_anchor": taught_anchor_exists,
        "initial_badges": first_assistant.skill_badges if first_assistant else [],
    }
    if next_step:
        data["pending_onboarding_step"] = next_step
    show_guide = (
        not request.user.dismissed_guide
        and timezone.now() - request.user.created_at <= timezone.timedelta(hours=1)
    )
    data["show_guide"] = show_guide
    return Response(data)


@api_view(["POST"])
@permission_classes([AllowAny])
def demo_login(request):
    User = get_user_model()
    user, _ = User.objects.get_or_create(username="demo")
    token = RefreshToken.for_user(user)
    return Response({"access": str(token.access_token), "refresh": str(token)})


@api_view(["POST"])
@permission_classes([AllowAny])
def demo_user(request):
    """Create a temporary demo user and return auth tokens."""
    User = get_user_model()
    username = f"guest_{uuid.uuid4().hex[:8]}"
    user = User.objects.create(username=username)
    for step in ONBOARDING_STEPS:
        record_step_completion(user, step)
    # create a simple demo assistant
    Assistant.objects.create(
        name="Demo Assistant",
        description="Temporary assistant",
        created_by=user,
        is_demo=True,
    )
    token = RefreshToken.for_user(user)
    return Response({"access": str(token.access_token), "refresh": str(token)})

