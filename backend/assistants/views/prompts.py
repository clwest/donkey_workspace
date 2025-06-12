from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from assistants.models.project import AssistantPromptLink
from assistants.serializers import AssistantPromptLinkSerializer
from prompts.serializers import PromptSerializer
from mcp_core.models import PromptUsageLog
from rest_framework.permissions import IsAuthenticated
from django.db import models
from prompts.models import Prompt
from assistants.models import Assistant, AssistantBootLog
from mcp_core.serializers import PromptUsageLogSerializer


@api_view(["GET"])
def linked_prompts(request, project_id):
    links = AssistantPromptLink.objects.filter(project_id=project_id)
    serializer = AssistantPromptLinkSerializer(links, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def link_prompt_to_project(request):
    serializer = AssistantPromptLinkSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def unlink_prompt_from_project(request, link_id):
    """Remove a prompt link from a project."""
    link = get_object_or_404(AssistantPromptLink, id=link_id)
    link.delete()
    return Response({"status": "deleted"})


@api_view(["GET"])
def recent_prompts(request):
    """Return a short list of recently used prompts."""
    logs = PromptUsageLog.objects.select_related("prompt").order_by("-created_at")[:20]

    prompts = []
    seen = set()
    for log in logs:
        if log.prompt and log.prompt_id not in seen:
            prompts.append(log.prompt)
            seen.add(log.prompt_id)

    serializer = PromptSerializer(prompts, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def available_prompts(request, slug):
    """Return prompts linked to this assistant by tag or document."""
    assistant = get_object_or_404(Assistant, slug=slug)
    docs = assistant.documents.all()
    prompts = Prompt.objects.filter(
        models.Q(tags__slug=assistant.slug)
        | models.Q(tags__name__iexact=assistant.name)
        | models.Q(assistant=assistant)
        | models.Q(source_document__in=docs)
    ).distinct()
    data = []
    for p in prompts:
        item = PromptSerializer(p).data
        logs = PromptUsageLog.objects.filter(prompt=p).order_by("-created_at")[:5]
        item["usage_logs"] = PromptUsageLogSerializer(logs, many=True).data
        data.append(item)
    return Response(data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_assistant_prompt(request, slug):
    """Assign a new system prompt to the assistant and reset boot logs."""
    assistant = get_object_or_404(Assistant, slug=slug)
    prompt_id = request.data.get("prompt_id")
    if not prompt_id:
        return Response({"error": "prompt_id required"}, status=400)
    try:
        prompt = Prompt.objects.get(id=prompt_id)
    except (ValueError, Prompt.DoesNotExist):
        return Response({"error": "Prompt not found"}, status=404)
    assistant.system_prompt = prompt
    assistant.prompt_title = prompt.title
    assistant.save(update_fields=["system_prompt", "prompt_title"])
    assistant.boot_logs.all().delete()
    return Response({"status": "updated"})
