from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models import (
    Assistant,
    SymbolicUXPlaybook,
    RoleDrivenUITemplate,
)
from assistants.serializers import (
    AssistantSerializer,
    SymbolicUXPlaybookSerializer,
    RoleDrivenUITemplateSerializer,
)


@api_view(["GET"])
@permission_classes([AllowAny])
def assistant_interface(request, assistant_id):
    """Return active interface configuration for an assistant."""
    assistant = get_object_or_404(Assistant, id=assistant_id)
    playbook = SymbolicUXPlaybook.objects.filter(archetype=assistant.specialty).first()
    template = RoleDrivenUITemplate.objects.filter(assigned_role=assistant.specialty).first()
    data = {
        "assistant": AssistantSerializer(assistant).data,
        "active_playbook": SymbolicUXPlaybookSerializer(playbook).data if playbook else None,
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
