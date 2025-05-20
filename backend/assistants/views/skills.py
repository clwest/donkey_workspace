from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from assistants.models import Assistant, AssistantSkill
from assistants.serializers import AssistantSkillSerializer
from tools.models import Tool


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def assistant_skills(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)

    if request.method == "GET":
        skills = assistant.skills.all()
        serializer = AssistantSkillSerializer(skills, many=True)
        return Response(serializer.data)

    data = request.data
    items = data if isinstance(data, list) else [data]
    created = []
    for item in items:
        name = item.get("name")
        if not name:
            continue
        skill, _ = AssistantSkill.objects.get_or_create(assistant=assistant, name=name)
        skill.description = item.get("description", skill.description)
        if item.get("confidence") is not None:
            skill.confidence = item["confidence"]
        tags = item.get("related_tags")
        if tags is not None:
            skill.related_tags = tags
        skill.save()
        if item.get("related_tools"):
            tools = Tool.objects.filter(slug__in=item["related_tools"])
            skill.related_tools.set(tools)
        created.append(skill)

    serializer = AssistantSkillSerializer(created, many=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
