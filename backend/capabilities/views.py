from django.http import JsonResponse
from django.urls import get_resolver, resolve
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .registry import CAPABILITY_REGISTRY, get_capabilities
from .models import CapabilityUsageLog
from assistants.models.assistant import Assistant


def capability_status(request):
    resolver = get_resolver()

    def collect(patterns, prefix=""):
        urls = []
        for p in patterns:
            if hasattr(p, "url_patterns"):
                urls.extend(collect(p.url_patterns, prefix + str(p.pattern)))
            else:
                urls.append(prefix + str(p.pattern))
        return urls

    all_urls = [u for u in collect(resolver.url_patterns) if str(u).startswith("api")]

    assistant_slug = request.GET.get("assistant") or request.GET.get("slug")
    assistant = None
    if assistant_slug:
        assistant = Assistant.objects.filter(slug=assistant_slug).first()

    data = []
    for key, info in CAPABILITY_REGISTRY.items():
        route_prefix = info.get("route", "")
        connected = any(url.startswith(route_prefix.lstrip("/")) for url in all_urls)
        enabled = None
        last_called = None
        if assistant:
            enabled = bool(assistant.capabilities.get(key))
            log = (
                CapabilityUsageLog.objects.filter(assistant=assistant, capability=key)
                .order_by("-created_at")
                .first()
            )
            if log:
                last_called = log.created_at
        data.append(
            {
                "key": key,
                "route": route_prefix,
                "connected": connected,
                "enabled": enabled,
                "last_called_at": last_called,
                "description": info.get("description", ""),
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
