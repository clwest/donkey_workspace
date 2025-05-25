"""Ontology and belief management API views."""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from mcp_core.utils.belief_cascade import generate_belief_cascade_graph
from mcp_core.utils.role_collision import detect_role_collisions
from mcp_core.utils.stabilization_campaigns import launch_stabilization_campaign


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


@api_view(["POST"])
@permission_classes([AllowAny])
def start_stabilization(request):
    """Launch a clause stabilization campaign."""
    clause_id = request.data.get("clause_id")
    return Response(launch_stabilization_campaign(clause_id))
