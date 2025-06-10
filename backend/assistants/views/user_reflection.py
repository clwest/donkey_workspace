from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models import Assistant
from memory.models import MemoryEntry
from memory.serializers import MemoryEntryFeedbackSerializer


class AssistantReflectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        assistant = get_object_or_404(Assistant, slug=slug)
        content = request.data.get("content")
        rating = request.data.get("rating")
        if not content:
            return Response({"error": "content is required"}, status=400)
        entry = MemoryEntry.objects.create(
            assistant=assistant,
            event=content,
            summary=content[:200],
            source_user=request.user,
            rating=rating,
            type="user_reflection",
        )
        serializer = MemoryEntryFeedbackSerializer(entry)
        return Response(serializer.data, status=201)
