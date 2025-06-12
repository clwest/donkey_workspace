from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models.assistant import Assistant
from assistants.models.thoughts import EmotionalResonanceLog
from assistants.serializers_pass import EmotionalResonanceLogSerializer
from assistants.tasks import reflect_on_emotional_resonance


@api_view(["GET"])
@permission_classes([AllowAny])
def assistant_empathy(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    logs = EmotionalResonanceLog.objects.filter(assistant=assistant).order_by("-created_at")[:20]
    return Response(EmotionalResonanceLogSerializer(logs, many=True).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def assistant_reflect_empathy(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    result = reflect_on_emotional_resonance.delay(str(assistant.id))
    return Response({"task": result.id})


@api_view(["GET"])
@permission_classes([AllowAny])
def memory_resonance(request, id):
    log = EmotionalResonanceLog.objects.filter(source_memory_id=id).order_by("-created_at").first()
    if not log:
        return Response({"error": "Not found"}, status=404)
    return Response(EmotionalResonanceLogSerializer(log).data)

