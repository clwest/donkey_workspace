from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from assistants.models.assistant import Assistant
from assistants.models.extensions import (
    HapticFeedbackChannel,
    AssistantSensoryExtensionProfile,
)
from assistants.serializers_pass import (
    HapticFeedbackChannelSerializer,
    AssistantSensoryExtensionProfileSerializer,
)
from assistants.utils.voice_commands import VoiceCodexCommandModule


@api_view(["POST"])
@permission_classes([AllowAny])
def codex_voice_command(request):
    """Process a voice command directed at the codex."""
    audio = request.data.get("audio")
    transcript = request.data.get("transcript")
    module = VoiceCodexCommandModule()
    if audio:
        transcript = module.transcribe(audio)
    if not transcript:
        return Response({"error": "transcript required"}, status=400)
    command = module.parse_command(transcript)
    return Response(command)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def assistant_sensory_profile(request, assistant_id):
    """Retrieve or update sensory profile for an assistant."""
    assistant = get_object_or_404(Assistant, id=assistant_id)
    profile, _ = AssistantSensoryExtensionProfile.objects.get_or_create(
        assistant=assistant
    )
    if request.method == "POST":
        profile.supported_modes = request.data.get(
            "supported_modes", profile.supported_modes
        )
        profile.feedback_triggers = request.data.get(
            "feedback_triggers", profile.feedback_triggers
        )
        profile.memory_response_style = request.data.get(
            "memory_response_style", profile.memory_response_style
        )
        profile.save()
    serializer = AssistantSensoryExtensionProfileSerializer(profile)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def haptic_ritual(request):
    """Simulate a ritual-triggered haptic feedback."""
    assistant_id = request.data.get("assistant_id")
    assistant = get_object_or_404(Assistant, id=assistant_id)
    serializer = HapticFeedbackChannelSerializer(data=request.data)
    if serializer.is_valid():
        channel = serializer.save(linked_assistant=assistant)
        return Response(
            HapticFeedbackChannelSerializer(channel).data,
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=400)

