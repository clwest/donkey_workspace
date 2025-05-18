from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from assistants.models import AssistantPromptLink
from assistants.serializers import AssistantPromptLinkSerializer


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
