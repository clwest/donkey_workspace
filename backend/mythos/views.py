from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.apps import apps
from django.shortcuts import get_object_or_404

from agents.models.lore import SwarmCodex
from agents.serializers import SwarmCodexSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def get_archetype_card(request, assistant_id):
    """Return placeholder archetype card data for an assistant."""
    return Response({"tone": "", "tags": []})


@api_view(["GET"])
@permission_classes([AllowAny])
def get_ritual_launchpads(request):
    """Return placeholder ritual launchpad data."""
    return Response([])


class SwarmCodexRootView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        codices = SwarmCodex.objects.all().order_by("-created_at")
        serializer = SwarmCodexSerializer(codices, many=True)
        return Response(serializer.data)


class CodexClauseMutatorView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, clause_id):
        """Preview or save a mutated codex clause."""
        return Response({"clause": str(clause_id), "status": "preview"})


class FaultInjectorView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Inject a symbolic fault for testing."""
        return Response({"status": "fault injected"})


class MemoryAlignmentSandboxView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, assistant_id):
        """Return placeholder memory cluster data."""
        return Response({"assistant": str(assistant_id), "clusters": []})

class CodexFragmentDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        try:
            Fragment = apps.get_model("agents", "CodexClauseFragment")
        except LookupError:
            return Response({"error": "model unavailable"}, status=404)
        fragment = get_object_or_404(Fragment, id=id)
        data = {"id": fragment.id, "clause_id": getattr(fragment, "clause_id", None), "text": fragment.text}
        return Response(data)


class RitualDecompositionDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        try:
            Plan = apps.get_model("agents", "RitualDecompositionPlan")
            Step = apps.get_model("agents", "DecomposedStepTrace")
        except LookupError:
            return Response({"error": "model unavailable"}, status=404)
        plan = get_object_or_404(Plan, id=id)
        steps = Step.objects.filter(plan=plan).order_by("id")
        data = {
            "id": plan.id,
            "ritual_id": getattr(plan, "ritual_id", None),
            "summary": getattr(plan, "summary", ""),
            "steps": [{"id": s.id, "text": getattr(s, "step_text", "")} for s in steps],
        }
        return Response(data)
