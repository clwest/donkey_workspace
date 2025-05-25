from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from assistants.models.project import AssistantPromptLink
from assistants.serializers import AssistantPromptLinkSerializer
from prompts.serializers import PromptSerializer
from mcp_core.models import PromptUsageLog


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
    logs = (
        PromptUsageLog.objects.select_related("prompt")
        .order_by("-created_at")[:20]
    )

    prompts = []
    seen = set()
    for log in logs:
        if log.prompt and log.prompt_id not in seen:
            prompts.append(log.prompt)
            seen.add(log.prompt_id)

    serializer = PromptSerializer(prompts, many=True)
    return Response(serializer.data)
