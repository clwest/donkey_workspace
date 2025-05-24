from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models.assistant import Assistant
from agents.models.inheritance import CodexInheritanceLink


@api_view(["GET"])
@permission_classes([AllowAny])
def codex_inheritance(request, assistant_id):
    assistant = get_object_or_404(Assistant, id=assistant_id)
    links = CodexInheritanceLink.objects.filter(child=assistant).order_by("-created_at")
    data = [
        {
            "mentor": link.mentor.id,
            "inherited_clauses": link.inherited_clauses,
            "mutated_clauses": link.mutated_clauses,
            "created_at": link.created_at,
        }
        for link in links
    ]
    return Response({"assistant": str(assistant.id), "inheritance": data})
