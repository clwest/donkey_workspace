from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models import Assistant
from assistants.helpers.growth import upgrade_growth_stage


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upgrade_growth(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    upgraded = upgrade_growth_stage(assistant)
    return Response(
        {
            "stage": assistant.growth_stage,
            "points": assistant.growth_points,
            "status": "upgraded" if upgraded else "no_change",
        }
    )
