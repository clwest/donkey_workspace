from django.http import JsonResponse
from django.urls import get_resolver
from .registry import CAPABILITY_REGISTRY


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

    data = []
    for key, info in CAPABILITY_REGISTRY.items():
        route_prefix = info.get("route", "")
        connected = any(url.startswith(route_prefix.lstrip("/")) for url in all_urls)
        data.append({"key": key, "route": route_prefix, "connected": connected, "description": info.get("description", "")})
    return JsonResponse({"capabilities": data})
