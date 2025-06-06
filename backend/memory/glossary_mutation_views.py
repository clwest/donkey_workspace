from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from memory.management.commands.generate_missing_mutations import (
    generate_missing_mutations_for_assistant,
)
from memory.management.commands.test_glossary_mutations import (
    run_glossary_mutation_tests,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def suggest_missing_mutations(request):
    slug = request.data.get("assistant")
    if not slug:
        return Response({"error": "assistant required"}, status=400)
    updated = generate_missing_mutations_for_assistant(slug)
    return Response({"updated": len(updated)})


@api_view(["POST"])
@permission_classes([AllowAny])
def test_glossary_mutations(request):
    slug = request.data.get("assistant")
    if not slug:
        return Response({"error": "assistant required"}, status=400)
    results = run_glossary_mutation_tests(slug)
    return Response({"tested": len(results)})
