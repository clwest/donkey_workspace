from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from agents.models import Agent, AgentFeedbackLog
from agents.serializers import AgentSerializer, AgentFeedbackLogSerializer
from agents.utils.agent_controller import update_agent_profile_from_feedback

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


@api_view(["GET"])
def agent_feedback_logs(request, id):
    agent = get_object_or_404(Agent, id=id)
    logs = AgentFeedbackLog.objects.filter(agent=agent).order_by("-created_at")
    serializer = AgentFeedbackLogSerializer(logs, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def update_agent_from_feedback(request, id):
    agent = get_object_or_404(Agent, id=id)
    records = request.data.get("feedback", [])
    if not isinstance(records, list):
        return Response({"error": "feedback must be a list"}, status=400)
    logs = []
    for item in records:
        log = AgentFeedbackLog.objects.create(
            agent=agent,
            task_id=item.get("task"),
            feedback_text=item.get("feedback_text", ""),
            feedback_type=item.get("feedback_type", "reflection"),
            score=item.get("score"),
        )
        logs.append(log)

    summary = update_agent_profile_from_feedback(agent, logs)
    return Response({"updated": True, "summary": summary})
