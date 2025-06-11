from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def badge_list(request):
    """Return placeholder badges list."""
    return Response([])
