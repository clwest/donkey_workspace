from django.http import JsonResponse
from django.urls import resolve
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .registry import CAPABILITY_REGISTRY, get_capabilities
from assistants.models.assistant import Assistant


def capability_status(request):
    """Return capability ↔ route diagnostics."""

    assistant_slug = request.GET.get("assistant") or request.GET.get("slug")
    assistant = None
    if assistant_slug:
        assistant = Assistant.objects.filter(slug=assistant_slug).first()

    data = []
    for key, info in CAPABILITY_REGISTRY.items():
        route = info.get("route")
        view_name = None
        status = "connected"

        if route:
            try:
                match = resolve(route.lstrip("/"))
                view_name = f"{match.func.__module__}.{match.func.__name__}"
            except Exception:
                status = "broken"
        else:
            status = "missing"

        if assistant and not assistant.capabilities.get(key):
            status = "disabled"

        data.append(
            {
                "capability": key,
                "route": route,
                "view": view_name,
                "status": status,
            }
        )

    return JsonResponse({"capabilities": data})


@api_view(["GET"])
def capability_status_view(request):
    from .registry import get_capabilities

    status = {}
    for cap, info in get_capabilities().items():
        route = info.get("route")
        if not route:
            status[cap] = {"connected": False, "reason": "No route defined"}
        else:
            try:
                match = resolve(route)
                status[cap] = {"connected": True, "view": match.view_name}
            except Exception as e:
                status[cap] = {"connected": False, "reason": str(e)}

    return Response(status)
