from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from agents.models import Agent
from agents.serializers import AgentSerializer

@api_view(["GET"])
def list_agents(request):
    agents = Agent.objects.all().order_by("created_at")
    serializer = AgentSerializer(agents, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def agent_detail_view(request, slug):
    try:
        agent = Agent.objects.get(slug=slug)
    except Agent.DoesNotExist:
        return Response({"error": "Agent not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = AgentSerializer(agent)
    return Response(serializer.data)