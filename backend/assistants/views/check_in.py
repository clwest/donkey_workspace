from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from openai import OpenAI

from assistants.models import Assistant

client = OpenAI()


class AssistantCheckInView(APIView):
    """Return quick suggestions for what the assistant should work on."""

    def get(self, request, assistant_id):
        assistant = get_object_or_404(Assistant, pk=assistant_id)
        message = "What should I work on today?"
        try:
            resp = client.chat.completions.create(
                model=assistant.preferred_model,
                messages=[
                    {"role": "system", "content": assistant.persona_summary or ""},
                    {"role": "user", "content": message},
                ],
            )
            suggestions = resp.choices[0].message.content
        except Exception as e:
            suggestions = f"Error generating suggestions: {e}"
        return Response({"suggestions": suggestions}, status=status.HTTP_200_OK)
