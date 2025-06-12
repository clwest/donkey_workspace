from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from assistants.models.assistant import Assistant
from assistants.utils.starter_chat import seed_chat_starter_memory
from memory.models import SymbolicMemoryAnchor
from memory.services.acquisition import update_anchor_acquisition
from agents.models.identity import SymbolicIdentityCard
from assistants.models.thoughts import AssistantThoughtLog
from assistants.serializers import AssistantSerializer
from agents.serializers import SymbolicIdentityCardSerializer

PATH_DEFAULTS = {
    "memory": {"tone": "reflective", "tag": "memory"},
    "codex": {"tone": "precise", "tag": "codex"},
    "ritual": {"tone": "observant", "tag": "ritual"},
}


def create_assistant_from_mythpath(
    path, name, archetype, *, user=None, avatar_style="robot", tone_profile="friendly"
):
    defaults = PATH_DEFAULTS.get(path, {"tone": "neutral", "tag": "general"})
    tone = defaults["tone"]
    tag = defaults["tag"]

    assistant = Assistant.objects.create(
        name=name,
        specialty=tag,
        tone=tone,
        avatar_style=avatar_style,
        tone_profile=tone_profile,
        created_by=user,
    )

    from assistants.models.user_profile import AssistantUserProfile
    from assistants.helpers.memory_helpers import ensure_welcome_memory

    if user:
        AssistantUserProfile.objects.get_or_create(user=user, assistant=assistant)
    ensure_welcome_memory(assistant)

    card = SymbolicIdentityCard.objects.create(
        assistant=assistant,
        archetype=archetype,
        symbolic_tags=[tag],
        myth_path=path,
        purpose_signature="",
    )

    AssistantThoughtLog.objects.create(
        assistant=assistant,
        thought="\U0001faa9 No reflections yet. Tap ‘Reflect’ to begin",
        thought_type="meta",
    )

    if not assistant.memories.exists():
        seed_chat_starter_memory(assistant)

    return assistant, card


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def onboarding_create_assistant(request):
    data = request.data
    assistant_info = data.get("assistant", {})
    identity_info = data.get("identity_card", {})

    name = assistant_info.get("name") or data.get("name")
    path = data.get("path") or identity_info.get("myth_path")
    archetype = identity_info.get("archetype", "")
    avatar_style = assistant_info.get("avatar_style", "robot")
    tone_profile = assistant_info.get("tone_profile", "friendly")

    if not name or not path:
        return Response({"error": "name and path required"}, status=400)

    assistant, card = create_assistant_from_mythpath(
        path,
        name,
        archetype,
        user=request.user if request.user.is_authenticated else None,
        avatar_style=avatar_style,
        tone_profile=tone_profile,
    )

    return Response(
        {
            "assistant": AssistantSerializer(assistant).data,
            "identity_card": SymbolicIdentityCardSerializer(card).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assistant_onboard(request, id):
    """Save identity card details for an assistant."""
    assistant = get_object_or_404(Assistant, id=id)

    assistant.archetype = request.data.get("archetype", assistant.archetype)
    assistant.dream_symbol = request.data.get("dream_symbol", assistant.dream_symbol)
    assistant.init_reflection = request.data.get(
        "init_reflection", assistant.init_reflection
    )
    assistant.save()

    text = assistant.init_reflection or ""
    if text:
        for anchor in SymbolicMemoryAnchor.objects.all():
            if anchor.label.lower() in text.lower() or anchor.slug in text.lower():
                update_anchor_acquisition(anchor, "exposed")

    return Response(AssistantSerializer(assistant).data)
