from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from assistants.models.assistant import CouncilSession, CouncilThought, Assistant
from assistants.serializers import (
    CouncilSessionSerializer,
    CouncilThoughtSerializer,
)
from assistants.tasks import run_council_deliberation, reflect_on_council



@api_view(["POST"])
def start_session(request):
    data = request.data
    session = CouncilSession.objects.create(
        topic=data.get("topic", "Untitled"),
        project_id=data.get("project"),
        linked_memory_id=data.get("linked_memory"),
        created_by_id=data.get("created_by"),
    )
    members = data.get("members", [])
    if members:
        qs = Assistant.objects.filter(id__in=members)
        session.members.set(qs)
    serializer = CouncilSessionSerializer(session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def session_respond(request, id):
    session = get_object_or_404(CouncilSession, id=id)
    serializer = CouncilThoughtSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(council_session=session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def session_reflect(request, id):
    reflect_on_council.delay(str(id))
    return Response({"status": "queued"})


@api_view(["GET"])
def session_detail(request, id):
    session = get_object_or_404(CouncilSession, id=id)
    return Response(CouncilSessionSerializer(session).data)


@api_view(["GET"])
def session_thoughts(request, id):
    session = get_object_or_404(CouncilSession, id=id)
    thoughts = session.thoughts.order_by("created_at")
    serializer = CouncilThoughtSerializer(thoughts, many=True)
    return Response(serializer.data)
