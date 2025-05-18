from rest_framework.decorators import api_view

from rest_framework.response import Response
from rest_framework import status

from assistants.models import (
    AssistantObjective,
)

from assistants.serializers import (
    AssistantObjectiveSerializer,
)


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
