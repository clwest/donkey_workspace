"""Ontology and belief management API views."""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from mcp_core.utils.belief_cascade import generate_belief_cascade_graph
from mcp_core.utils.role_collision import detect_role_collisions
from mcp_core.utils.stabilization_campaigns import launch_stabilization_campaign
from codex.stabilization_logic import finalize_campaign
from django.apps import apps


@api_view(["GET"])
@permission_classes([AllowAny])
def cascade_graph(request, clause_id):
    """Return a belief cascade graph for a codex clause."""
    return Response(generate_belief_cascade_graph(clause_id))


@api_view(["GET"])
@permission_classes([AllowAny])
def swarm_collisions(request):
    """Detect narrative role collisions across assistants."""
    return Response(detect_role_collisions())


@api_view(["GET"])
@permission_classes([AllowAny])
def codex_clauses(request):
    """Return simple list of codex clauses."""
    Clause = apps.get_model("agents", "CodexClause")
    clauses = Clause.objects.all().order_by("id")
    data = [{"id": c.id, "text": c.text} for c in clauses]
    return Response(data)


@api_view(["POST"])
@permission_classes([AllowAny])
def start_stabilization(request):
    """Launch a clause stabilization campaign."""
    clause_id = request.data.get("clause_id")
    try:
        result = launch_stabilization_campaign(clause_id)
    except ValueError as e:
        return Response({"error": str(e)}, status=400)
    return Response(result)


@api_view(["POST"])
@permission_classes([AllowAny])
def finalize_stabilization_campaign(request, campaign_id):
    """Finalize the clause stabilization campaign."""
    return Response(finalize_campaign(campaign_id))
