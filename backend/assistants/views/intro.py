from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models import Assistant
from assistants.serializers import AssistantIntroSerializer
from assistants.helpers.intro import get_intro_splash_payload


class AssistantIntroView(APIView):
    """Return intro splash data for an assistant."""

    def get(self, request, slug):
        assistant = get_object_or_404(Assistant, slug=slug)
        data = get_intro_splash_payload(assistant)
        serializer = AssistantIntroSerializer(assistant)
        data.update(serializer.data)
        return Response(data)
