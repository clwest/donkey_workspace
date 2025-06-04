from django.urls import get_resolver
from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
import inspect
from capabilities.registry import get_capability_for_path


@api_view(["GET"])
@never_cache
def full_route_map(request):
    urlconf = get_resolver()
    routes = []

    for pattern in urlconf.url_patterns:
        try:
            callback = pattern.callback
            view_name = callback.__name__
            module_name = inspect.getmodule(callback).__name__
            pattern_str = str(pattern.pattern)

            routes.append(
                {
                    "path": pattern_str,
                    "view": view_name,
                    "module": module_name,
                    "name": getattr(pattern, "name", None),
                    "capability": get_capability_for_path(pattern_str),
                }
            )
        except Exception as e:
            routes.append(
                {
                    "path": str(pattern.pattern),
                    "error": str(e),
                }
            )

    return Response({"routes": routes})
