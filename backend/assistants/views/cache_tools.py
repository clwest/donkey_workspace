from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from assistants.models import Assistant
from assistants.helpers.redis_helpers import set_cached_reflection


@api_view(["POST"])
def flush_reflection_cache(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    set_cached_reflection(assistant.slug, None)
    return Response({"message": f"Reflection cache flushed for {assistant.slug}"})
