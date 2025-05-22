from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from assistants.models.assistant import Assistant
from assistants.models.core import AssistantMythLayer
from agents.models.lore import SwarmJournalEntry
from assistants.serializers import AssistantMythLayerSerializer
from agents.serializers import SwarmJournalEntrySerializer
from mcp_core.models import Tag


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def assistant_myth_layer(request, slug):
    """Retrieve or update myth layer for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)

    if request.method == "POST":
        origin_story = request.data.get("origin_story", "")
        legendary_traits = request.data.get("legendary_traits", {})
        myth, _ = AssistantMythLayer.objects.update_or_create(
            assistant=assistant,
            defaults={"origin_story": origin_story, "legendary_traits": legendary_traits},
        )
        return Response(
            AssistantMythLayerSerializer(myth).data, status=status.HTTP_201_CREATED
        )

    myth, _ = AssistantMythLayer.objects.get_or_create(assistant=assistant)
    return Response(AssistantMythLayerSerializer(myth).data)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def assistant_journals(request, slug):
    """List or create journal entries for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)

    if request.method == "POST":
        content = request.data.get("content", "")
        tag_ids = request.data.get("tags", [])
        is_private = request.data.get("is_private", True)
        season_tag = request.data.get("season_tag", "")

        entry = SwarmJournalEntry.objects.create(
            author=assistant,
            content=content,
            is_private=is_private,
            season_tag=season_tag,
        )
        if tag_ids:
            entry.tags.set(Tag.objects.filter(id__in=tag_ids))
        return Response(
            SwarmJournalEntrySerializer(entry).data, status=status.HTTP_201_CREATED
        )

    qs = SwarmJournalEntry.objects.filter(author=assistant).order_by("-created_at")
    serializer = SwarmJournalEntrySerializer(qs, many=True)
    return Response(serializer.data)
