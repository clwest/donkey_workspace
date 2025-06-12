from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models.assistant import Assistant, AssistantReputation
from assistants.serializers import AssistantReputationSerializer


@api_view(["GET"])
def assistant_reputation(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    rep, _ = AssistantReputation.objects.get_or_create(assistant=assistant)
    serializer = AssistantReputationSerializer(rep)
    return Response(serializer.data)
