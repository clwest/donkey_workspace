from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from assistants.models import Assistant, AssistantUserPreferences
from assistants.serializers import AssistantUserPreferencesSerializer

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def assistant_preferences(request, slug):
    """Return or update user preferences for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    profile, _ = AssistantUserPreferences.objects.get_or_create(
        user=request.user, assistant=assistant
    )
    if request.method == "POST":
        serializer = AssistantUserPreferencesSerializer(
            profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
    else:
        serializer = AssistantUserPreferencesSerializer(profile)
    return Response(serializer.data)
