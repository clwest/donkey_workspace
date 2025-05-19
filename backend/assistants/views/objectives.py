from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from prompts.utils.openai_utils import complete_chat

from rest_framework.response import Response
from rest_framework import status

from assistants.models import (
    AssistantObjective,
    AssistantThoughtLog,
)

from assistants.serializers import (
    AssistantObjectiveSerializer,
    AssistantObjectiveWithTasksSerializer,
)
from assistants.models import Assistant, AssistantProject


# Assistant Objectives
@api_view(["GET", "POST"])
def assistant_objectives(request, project_id):
    if request.method == "GET":
        objectives = AssistantObjective.objects.filter(project_id=project_id)
        serializer = AssistantObjectiveSerializer(objectives, many=True)
        return Response(serializer.data)
    if request.method == "POST":
        serializer = AssistantObjectiveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project_id=project_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def objectives_for_assistant(request, slug):
    """Return objectives for the assistant's most recent project."""
    try:
        assistant = Assistant.objects.get(slug=slug)
    except Assistant.DoesNotExist:
        return Response({"error": "Assistant not found"}, status=404)

    project = (
        AssistantProject.objects.filter(assistant=assistant)
        .order_by("-created_at")
        .first()
    )
    if not project:
        return Response([], status=200)

    objectives = AssistantObjective.objects.filter(project=project)
    serializer = AssistantObjectiveWithTasksSerializer(objectives, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def reflect_to_objectives(request, slug):
    """Infer new objectives from recent assistant thoughts."""
    assistant = get_object_or_404(Assistant, slug=slug)

    project_id = request.data.get("project_id")
    if project_id:
        project = get_object_or_404(
            AssistantProject, id=project_id, assistant=assistant
        )
    else:
        project = assistant.current_project or AssistantProject.objects.filter(
            assistant=assistant
        ).order_by("-created_at").first()

    max_thoughts = int(request.data.get("max_thoughts", 15))

    thoughts_qs = AssistantThoughtLog.objects.filter(
        assistant=assistant,
        thought_type__in=["generated", "reflection", "planning"],
    )
    if project:
        thoughts_qs = thoughts_qs.filter(project=project)

    thoughts = list(thoughts_qs.order_by("-created_at")[:max_thoughts])
    if not thoughts:
        return Response([], status=200)

    thought_text = "\n".join(t.thought.strip() for t in thoughts if t.thought)

    prompt = (
        "The following are internal thoughts of an assistant working on a project. "
        "Based on these thoughts, infer what objectives the assistant should pursue next.\n"
        "Return a list of 3-5 specific and actionable objectives.\n\n"
        f"Thoughts:\n{thought_text}"
    )

    result = complete_chat(system="", user=prompt)
    lines = [l.strip("-\u2022 ").strip() for l in result.splitlines() if l.strip()]
    created = []
    for line in lines:
        if ":" in line:
            title, desc = line.split(":", 1)
        else:
            title, desc = line, ""
        obj = AssistantObjective.objects.create(
            assistant=assistant,
            project=project,
            title=title.strip(),
            description=desc.strip(),
        )
        created.append(obj)

    serializer = AssistantObjectiveSerializer(created, many=True)
    return Response(serializer.data, status=201)
