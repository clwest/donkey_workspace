from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from assistants.utils.assistant_thought_engine import AssistantThoughtEngine

from project.models import Project, ProjectTask
from project.serializers import ProjectTaskSerializer
from assistants.serializers import AssistantTaskSerializer
from django.shortcuts import get_object_or_404
from assistants.models import (
    Assistant,
    AssistantObjective,
    AssistantProject,
    AssistantTask,
    AssistantThoughtLog,
)
from memory.models import MemoryEntry
from assistants.utils.task_generation import (
    generate_task_from_memory,
    generate_task_from_thought,
)


# Assistant Next Actions
@api_view(["GET", "POST"])
def assistant_next_actions(request, objective_id):
    if request.method == "GET":
        actions = AssistantNextAction.objects.filter(objective_id=objective_id)
        serializer = AssistantNextActionSerializer(actions, many=True)
        return Response(serializer.data)
    if request.method == "POST":
        serializer = AssistantNextActionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(objective_id=objective_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST"])
def assistant_project_tasks(request, project_id):
    try:
        assistant_project = AssistantProject.objects.get(pk=project_id)
    except AssistantProject.DoesNotExist:
        return Response({"error": "Project not found"}, status=404)

    project = Project.objects.filter(assistant_project=assistant_project).first()
    if project is None:
        return Response({"error": "Linked project not found"}, status=404)

    if request.method == "GET":
        tasks = ProjectTask.objects.filter(project=project).order_by("priority")
        serializer = ProjectTaskSerializer(tasks, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        serializer = ProjectTaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project=project)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)




@api_view(["POST"])
def generate_assistant_project_thought(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({"error": "Project not found."}, status=404)

    engine = AssistantThoughtEngine(assistant=project.assistant, project=project)
    result = engine.think()

    return Response(
        {
            "thought": result["thought"],
            "steps": result.get("steps"),
            "model": result.get("model"),
            "created_at": result.get("created_at"),
        }
    )


@api_view(["PATCH", "DELETE"])
def update_or_delete_task(request, task_id):
    try:
        task = ProjectTask.objects.get(pk=task_id)
    except ProjectTask.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "PATCH":
        serializer = ProjectTaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




@api_view(["PATCH", "DELETE"])
def assistant_project_task_detail(request, task_id):
    try:
        task = ProjectTask.objects.get(pk=task_id)
    except ProjectTask.DoesNotExist:
        return Response({"error": "Task not found"}, status=404)

    if request.method == "PATCH":
        serializer = ProjectTaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == "DELETE":
        task.delete()
        return Response(status=204)


@api_view(["POST"])
def plan_tasks_for_objective(request, slug, objective_id):
    """Generate tasks for an objective using the thought engine."""
    try:
        assistant = Assistant.objects.get(slug=slug)
        objective = AssistantObjective.objects.get(id=objective_id, assistant=assistant)
    except (Assistant.DoesNotExist, AssistantObjective.DoesNotExist):
        return Response({"error": "Not found"}, status=404)

    engine = AssistantThoughtEngine(assistant=assistant, project=objective.project)
    tasks = engine.plan_tasks_from_objective(objective)
    serializer = AssistantTaskSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def propose_task(request, slug):
    """Generate a proposed task from a memory or thought."""
    try:
        assistant = Assistant.objects.get(slug=slug)
    except Assistant.DoesNotExist:
        return Response({"error": "Assistant not found"}, status=404)

    memory_id = request.data.get("memory_id")
    thought_id = request.data.get("thought_id")
    project_id = request.data.get("project_id")

    project = None
    if project_id:
        project = get_object_or_404(AssistantProject, id=project_id, assistant=assistant)

    if memory_id:
        memory = get_object_or_404(MemoryEntry, id=memory_id)
        project = project or memory.related_project or assistant.current_project
        suggestion = generate_task_from_memory(memory)
        source_type = "memory"
        source_id = memory.id
    elif thought_id:
        thought = get_object_or_404(AssistantThoughtLog, id=thought_id)
        project = project or thought.project or assistant.current_project
        suggestion = generate_task_from_thought(thought)
        source_type = "thought"
        source_id = thought.id
    else:
        return Response({"error": "memory_id or thought_id required"}, status=400)

    if not project:
        return Response({"error": "Project context required"}, status=400)

    task = AssistantTask.objects.create(
        project=project,
        title=suggestion.get("title"),
        notes=suggestion.get("notes", ""),
        source_type=source_type,
        source_id=source_id,
        proposed_by=assistant,
    )

    serializer = AssistantTaskSerializer(task)
    return Response(serializer.data, status=201)
