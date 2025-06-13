import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from memory.management.commands.generate_missing_mutations import (
    generate_missing_mutations_for_assistant,
)
from memory.management.commands.test_glossary_mutations import (
    run_glossary_mutation_tests,
)


logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([IsAuthenticated])


def suggest_missing_mutations(request):
    slug = request.data.get("assistant")
    if not slug:
        return Response({"error": "assistant required"}, status=400)
    try:
        updated, stats = generate_missing_mutations_for_assistant(slug)
    except Exception as exc:
        logger.exception("suggest_missing_mutations error")
        return Response({"error": str(exc)}, status=500)
    return Response({"updated": len(updated), "stats": stats})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def test_glossary_mutations(request):
    slug = request.data.get("assistant")
    if not slug:
        return Response({"error": "assistant required"}, status=400)
    results = run_glossary_mutation_tests(slug)
    return Response({"tested": len(results)})
