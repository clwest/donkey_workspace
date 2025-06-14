from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def rate_limit_inspector(request):
    """Return simple throttle counters for the current user."""
    prefix = f"ratelimit:{request.user.id}:"
    counts = {}
    internal_cache = getattr(cache, "_cache", {})
    for key in internal_cache:
        if key.startswith(prefix):
            parts = key.split(":")
            if len(parts) >= 3:
                endpoint = parts[2]
                counts[endpoint] = internal_cache.get(key, 0)
    return Response({"user": request.user.id, "counts": counts})
