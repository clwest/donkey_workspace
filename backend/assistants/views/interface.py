from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models import (
    Assistant,
    SymbolicUXPlaybook,
    RoleDrivenUITemplate,
    SymbolicToolkitRegistry,
)
from assistants.serializers_pass import (
    AssistantSerializer,
    SymbolicUXPlaybookSerializer,
    RoleDrivenUITemplateSerializer,
    SymbolicToolkitRegistrySerializer,
)
from assistants.utils.interface_adaptation import compute_adaptation_state


@api_view(["GET"])
@permission_classes([AllowAny])
def assistant_interface(request, assistant_id):
    """Return active interface configuration for an assistant."""
    assistant = get_object_or_404(Assistant, id=assistant_id)
    playbook = SymbolicUXPlaybook.objects.filter(archetype=assistant.specialty).first()
    template = RoleDrivenUITemplate.objects.filter(
        assigned_role=assistant.specialty
    ).first()
    data = {
        "assistant": AssistantSerializer(assistant).data,
        "active_playbook": (
            SymbolicUXPlaybookSerializer(playbook).data if playbook else None
        ),
        "template": RoleDrivenUITemplateSerializer(template).data if template else None,
        "adaptation_layer": compute_adaptation_state(assistant),
    }
    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def new_assistant_interface(request):
    """Return default interface data for creating a new assistant."""
    playbook = SymbolicUXPlaybook.objects.first()
    template = RoleDrivenUITemplate.objects.first()
    data = {
        "assistant": {"name": "New Assistant"},
        "active_playbook": (
            SymbolicUXPlaybookSerializer(playbook).data if playbook else None
        ),
        "template": RoleDrivenUITemplateSerializer(template).data if template else None,
    }
    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def ux_playbooks(request):
    """List all UX playbooks."""
    playbooks = SymbolicUXPlaybook.objects.all()
    return Response(SymbolicUXPlaybookSerializer(playbooks, many=True).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def role_template(request, role):
    """Retrieve default template for a given role."""
    template = get_object_or_404(RoleDrivenUITemplate, assigned_role=role)
    return Response(RoleDrivenUITemplateSerializer(template).data)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def symbolic_toolkits(request):
    """Retrieve or create a symbolic toolkit for a user."""
    if request.method == "GET":
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response({"error": "user_id required"}, status=400)
        toolkit, _ = SymbolicToolkitRegistry.objects.get_or_create(user_id=user_id)
        return Response(SymbolicToolkitRegistrySerializer(toolkit).data)

    serializer = SymbolicToolkitRegistrySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    toolkit = serializer.save()
    return Response(SymbolicToolkitRegistrySerializer(toolkit).data, status=201)


@api_view(["GET"])
@permission_classes([AllowAny])
def ritual_intuition_panel(request):
    """Provide assistant-guided ritual intuition data."""
    suggestion = "Now is the time to Anchor."
    data = {
        "symbolic_readiness": 0.5,
        "suggestion": suggestion,
        "confidence": 0.5,
    }
    return Response(data)
