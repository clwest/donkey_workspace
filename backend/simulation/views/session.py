from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..models import MythflowSession, SymbolicDialogueExchange
from ..serializers import (
    MythflowSessionSerializer,
    SymbolicDialogueExchangeSerializer,
)
from assistants.models import Assistant
from agents.models.identity import SymbolicIdentityCard


class MythflowSessionViewSet(viewsets.ModelViewSet):
    queryset = MythflowSession.objects.all().order_by("-created_at")
    serializer_class = MythflowSessionSerializer


class SymbolicDialogueExchangeViewSet(viewsets.ModelViewSet):
    queryset = SymbolicDialogueExchange.objects.all().order_by("-created_at")
    serializer_class = SymbolicDialogueExchangeSerializer


class RoleplayPersonaModuleView(APIView):
    def get(self, request):
        assistant_id = request.query_params.get("assistant_id")
        if not assistant_id:
            return Response({"detail": "assistant_id required"}, status=400)
        assistant = get_object_or_404(Assistant, pk=assistant_id)
        card = SymbolicIdentityCard.objects.filter(assistant=assistant).first()
        data = {
            "assistant": assistant.id,
            "name": assistant.name,
            "specialty": assistant.specialty,
            "archetype": card.archetype if card else None,
            "purpose_signature": card.purpose_signature if card else None,
        }
        return Response(data)
