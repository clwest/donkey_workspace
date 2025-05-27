from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle
from prompts.models import PromptUsageTemplate
from prompts.serializers import PromptUsageTemplateSerializer
from mcp_core.serializers import PromptUsageLogSerializer


@api_view(["POST"])
def create_prompt_template(request):
    serializer = PromptUsageTemplateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(["GET"])
def list_prompt_templates(request):
    templates = PromptUsageTemplate.objects.filter(is_active=True).order_by(
        "agent", "priority"
    )
    serializer = PromptUsageTemplateSerializer(templates, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def prompt_template_detail(request, pk):
    try:
        template = PromptUsageTemplate.objects.get(pk=pk)
    except PromptUsageTemplate.DoesNotExist:
        return Response(
            {"error": "Template not found"}, status=status.HTTP_404_NOT_FOUND
        )
    serializer = PromptUsageTemplateSerializer(template)
    return Response(serializer.data)


@api_view(["PATCH"])
def update_prompt_template(request, pk):
    try:
        template = PromptUsageTemplate.objects.get(pk=pk)
    except PromptUsageTemplate.DoesNotExist:
        return Response({"error": "Template not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = PromptUsageTemplateSerializer(template, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(["DELETE"])
def delete_prompt_template(request, pk):
    try:
        template = PromptUsageTemplate.objects.get(pk=pk)
    except PromptUsageTemplate.DoesNotExist:
        return Response({"error": "Template not found"}, status=status.HTTP_404_NOT_FOUND)
    template.delete()
    return Response(status=204)


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([UserRateThrottle])
def log_prompt_usage_view(request):
    print("Incoming Prompt Usage Payload:", request.data)
    serializer = PromptUsageLogSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
