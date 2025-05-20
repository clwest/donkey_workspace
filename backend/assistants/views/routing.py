from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from assistants.utils.routing_suggestion import suggest_assistant_for_context


@api_view(["POST"])
@permission_classes([AllowAny])
def suggest_assistant(request):
    """Suggest an assistant based on context summary and tags."""

    context_summary = request.data.get("context_summary", "")
    tags = request.data.get("tags", []) or []
    recent_messages = request.data.get("recent_messages", []) or []

    result = suggest_assistant_for_context(context_summary, tags, recent_messages)
    if not result:
        return Response({"suggested_assistant": None, "confidence": 0.0})

    best = result["best"]
    alternates = result.get("alternates", [])

    def brief(a):
        return {"name": a.name, "slug": a.slug, "specialty": a.specialty}

    return Response(
        {
            "suggested_assistant": brief(best["assistant"]),
            "confidence": round(best["score"], 3),
            "reasoning": best.get("reason", ""),
            "alternate_suggestions": [
                {"assistant": brief(r["assistant"]), "score": round(r["score"], 3)}
                for r in alternates
            ],
        }
    )
