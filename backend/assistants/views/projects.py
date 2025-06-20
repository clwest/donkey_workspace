from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from assistants.models.project import (
    AssistantProject,
    AssistantProjectRole,
    ProjectPlanningLog,
    AssistantObjective,
    AssistantTask
)
from assistants.serializers import (
    AssistantProjectSerializer,
    AssistantFromPromptSerializer,
    AssistantSerializer,
    AssistantProjectRoleSerializer,
    ProjectPlanningLogSerializer,
)
from django.utils.text import slugify
from assistants.models.assistant import Assistant, ChatSession
from prompts.models import Prompt
from prompts.utils.embeddings import get_prompt_embedding
from embeddings.helpers.helpers_io import save_embedding
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from memory.services import MemoryService
from assistants.services import AssistantService
from project.models import ProjectMemoryLink, ProjectMilestone
from assistants.helpers.mood import get_session_mood, map_mood_to_tone
from assistants.utils.memory_project_planner import build_project_plan_from_memories
from assistants.utils.assistant_thought_engine import AssistantThoughtEngine
import uuid


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def assistant_projects(request):
    if request.method == "GET":
        projects = (
            AssistantProject.objects.all()
            .select_related("assistant")
            .prefetch_related("objectives")
            .order_by("-created_at")
        )
        serializer = AssistantProjectSerializer(projects, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = AssistantProjectSerializer(data=request.data)

        if serializer.is_valid():
            project = serializer.save()
            return Response(
                AssistantProjectSerializer(project).data, status=status.HTTP_201_CREATED
            )
        else:
            print("🚨 Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([AllowAny])
def assistant_project_detail(request, pk):
    try:
        project = AssistantProject.objects.get(pk=pk)
    except AssistantProject.DoesNotExist:
        return Response({"error": "Project not found"}, status=404)

    if request.method == "GET":
        serializer = AssistantProjectSerializer(project)
        return Response(serializer.data)

    if request.method == "PATCH":
        serializer = AssistantProjectSerializer(
            project, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    project.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([AllowAny])
def bootstrap_assistant_from_prompt(request):
    serializer = AssistantFromPromptSerializer(
        data=request.data, context={"request": request}
    )
    serializer.is_valid(raise_exception=True)
    result = serializer.save()

    assistant_data = AssistantSerializer(result["assistant"]).data
    project_data = AssistantProjectSerializer(result["project"]).data

    return Response(
        {
            "assistant": assistant_data,
            "project": project_data,
        },
        status=201,
    )


@api_view(["GET"])
def projects_for_assistant(request, slug):
    try:
        assistant = Assistant.objects.get(slug=slug)
    except Assistant.DoesNotExist:
        return Response({"error": "Assistant not found"}, status=404)

    projects = AssistantProject.objects.filter(assistant=assistant)
    serializer = AssistantProjectSerializer(projects, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def assign_project(request, slug):
    """Assign an assistant's active project."""
    try:
        assistant = Assistant.objects.get(slug=slug)
    except Assistant.DoesNotExist:
        return Response({"error": "Assistant not found"}, status=404)

    project_id = request.data.get("project_id")
    if not project_id:
        return Response({"error": "project_id required"}, status=400)

    try:
        project = AssistantProject.objects.get(id=project_id)
    except AssistantProject.DoesNotExist:
        return Response({"error": "Project not found"}, status=404)

    if project.assistant != assistant:
        return Response(
            {"error": "Project does not belong to this assistant"}, status=400
        )

    assistant.current_project = project
    assistant.save()
    return Response({"status": "assigned"})


@api_view(["GET", "POST"])
def project_roles(request, project_id):
    """List or create roles for a project."""
    if request.method == "GET":
        roles = AssistantProjectRole.objects.filter(
            project_id=project_id
        ).select_related("assistant")
        serializer = AssistantProjectRoleSerializer(roles, many=True)
        return Response(serializer.data)

    serializer = AssistantProjectRoleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(project_id=project_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH", "DELETE"])
def project_role_detail(request, role_id):
    try:
        role = AssistantProjectRole.objects.get(id=role_id)
    except AssistantProjectRole.DoesNotExist:
        return Response({"error": "Role not found"}, status=404)

    if request.method == "PATCH":
        serializer = AssistantProjectRoleSerializer(
            role, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    role.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def project_history(request, project_id):
    """Return planning log timeline for a project."""
    logs = ProjectPlanningLog.objects.filter(project_id=project_id).order_by(
        "-timestamp"
    )
    serializer = ProjectPlanningLogSerializer(logs, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def create_project_from_memory(request, slug=None):
    """Create a new assistant project based on a memory entry."""
    data = request.data
    if slug:
        assistant = get_object_or_404(Assistant, slug=slug)
    else:
        assistant = get_object_or_404(Assistant, id=data.get("assistant_id"))
    memory_id = data.get("memory_id")
    memory = MemoryService.get_entry_or_404(memory_id)

    title = data.get(
        "title", f"Project from memory: {memory.summary or memory.event[:50]}"
    )

    project, created = AssistantProject.objects.get_or_create(
        assistant=assistant,
        title=title,
        defaults={"created_by": assistant.created_by},
    )

    if created:
        User = get_user_model()
        user = request.user if request.user.is_authenticated else assistant.created_by
        if not user:
            user = User.objects.first()

        core_project = AssistantService.create_project(
            user=user,
            title=title,
            assistant=assistant,
            assistant_project=project,
            created_from_memory=memory,
        )

        ProjectMemoryLink.objects.create(project=core_project, memory=memory)

    AssistantObjective.objects.create(
        assistant=assistant,
        project=project,
        title="Build a project based on the memory provided.",
        description=memory.summary or memory.event[:300],
        source_memory=memory,
    )

    return Response({"project_id": project.id, "slug": project.slug}, status=201)


@api_view(["POST"])
@permission_classes([AllowAny])
def memory_to_project(request, slug):
    """Create a new project plan from selected memory entries."""
    try:
        assistant = Assistant.objects.get(slug=slug)
    except Assistant.DoesNotExist:
        return Response({"error": "Assistant not found"}, status=404)

    memory_ids = request.data.get("memory_ids") or []
    if not isinstance(memory_ids, list) or not memory_ids:
        return Response({"error": "memory_ids required"}, status=400)

    memories = list(MemoryService.filter_entries(id__in=memory_ids))
    if not memories:
        return Response({"error": "No memories found"}, status=400)

    planning_style = request.data.get("planning_style", "bullet")
    title = request.data.get("project_title")

    plan = build_project_plan_from_memories(memories, planning_style, title)

    project = AssistantProject.objects.create(
        assistant=assistant,
        title=plan["title"],
        description="Project generated from memory entries.",
        created_by=request.user if request.user.is_authenticated else None,
    )

    User = get_user_model()
    user = request.user if request.user.is_authenticated else User.objects.first()
    core_project = AssistantService.create_project(
        user=user,
        title=plan["title"],
        assistant=assistant,
        assistant_project=project,
    )

    for mem in memories:
        ProjectMemoryLink.objects.create(project=core_project, memory=mem)

    objectives = []
    for obj_title in plan["objectives"]:
        obj = AssistantObjective.objects.create(
            project=project,
            assistant=assistant,
            title=obj_title,
        )
        objectives.append(obj)
        session = (
            ChatSession.objects.filter(
                assistant=assistant,
                project__assistant_project=project,
            )
            .order_by("-created_at")
            .first()
        )
        mood = get_session_mood(session)
        tone = map_mood_to_tone(mood)
        AssistantTask.objects.create(
            project=project,
            objective=obj,
            title=f"Task for {obj_title}",
            tone=tone,
            generated_from_mood=mood,
        )

    for ms in plan.get("milestones", []):
        ProjectMilestone.objects.create(
            project=core_project,
            title=ms.get("title"),
            description=ms.get("description", ""),
        )

    return Response({"project_id": str(project.id)}, status=201)


@api_view(["POST"])
def regenerate_project_plan(request, pk):
    """Regenerate a project's plan from recent memories."""
    try:
        project = AssistantProject.objects.get(id=pk)
    except AssistantProject.DoesNotExist:
        return Response({"error": "Project not found"}, status=404)

    reason = request.data.get("reason", "memory_shift")
    project.regenerate_project_plan_from_memory(reason=reason)
    return Response({"status": "regenerated"})


@api_view(["GET"])
def project_memory_changes(request, pk):
    """Return recent memory events considered for regeneration."""
    try:
        project = AssistantProject.objects.get(id=pk)
    except AssistantProject.DoesNotExist:
        return Response({"error": "Project not found"}, status=404)

    memories = (
        MemoryService.filter_entries(assistant=project.assistant)
        .order_by("-created_at")[:5]
    )
    data = [
        {"id": str(m.id), "event": m.event, "importance": m.importance}
        for m in memories
    ]
    return Response(data)


@api_view(["POST"])
def generate_project_mission(request):
    """Generate a mission statement for a project."""
    project_id = request.data.get("project_id")
    if not project_id:
        return Response({"error": "project_id required"}, status=400)
    project = get_object_or_404(AssistantProject, id=project_id)
    engine = AssistantThoughtEngine(assistant=project.assistant, project=project)
    result = engine.generate_project_mission()
    return Response(result)


@api_view(["POST"])
def generate_tasks_for_project(request, project_id):
    """Generate tasks for the given project."""
    project = get_object_or_404(AssistantProject, id=project_id)
    engine = AssistantThoughtEngine(assistant=project.assistant, project=project)
    result = engine.plan_project_tasks()
    return Response(result)


@api_view(["POST"])
def ai_plan_project(request, pk):
    """Return an AI generated plan for the project."""
    project = get_object_or_404(AssistantProject, id=pk)
    engine = AssistantThoughtEngine(assistant=project.assistant, project=project)
    result = engine.plan_project_tasks()
    return Response(result)
