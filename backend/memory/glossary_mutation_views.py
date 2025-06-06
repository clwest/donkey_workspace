from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from memory.management.commands.generate_missing_mutations import (
    generate_missing_mutations_for_assistant,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def suggest_missing_mutations(request):
    slug = request.data.get("assistant")
    if not slug:
        return Response({"error": "assistant required"}, status=400)
    updated = generate_missing_mutations_for_assistant(slug)
    return Response({"updated": len(updated)})
