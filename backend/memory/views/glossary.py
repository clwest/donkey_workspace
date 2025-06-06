from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from memory.models import SymbolicMemoryAnchor


@api_view(["POST"])
def accept_mutation(request, id):
    """Mark a glossary mutation as accepted."""
    anchor = get_object_or_404(SymbolicMemoryAnchor, id=id)
    if getattr(anchor, "status", None) == "pending":
        anchor.status = "accepted"
        anchor.save(update_fields=["status"])
    return Response({"status": anchor.status})

