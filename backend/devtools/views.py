from django.urls import get_resolver, URLPattern, URLResolver
from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import inspect
from capabilities.registry import get_capability_for_path
import subprocess
import json
from pathlib import Path
from django.forms.models import model_to_dict


def _walk_patterns(patterns, prefix=""):
    routes = []
    for p in patterns:
        if isinstance(p, URLResolver):
            routes.extend(_walk_patterns(p.url_patterns, prefix + str(p.pattern)))
        elif isinstance(p, URLPattern):
            try:
                callback = p.callback
                route = prefix + str(p.pattern)
                routes.append(
                    {
                        "path": route,
                        "view": callback.__name__,
                        "module": inspect.getmodule(callback).__name__,
                        "name": getattr(p, "name", None),
                        "capability": get_capability_for_path(route),
                    }
                )
            except Exception as e:
                routes.append({"path": prefix + str(p.pattern), "error": str(e)})
    return routes


def get_full_route_map():
    resolver = get_resolver()
    return _walk_patterns(resolver.url_patterns)


class RouteInspector:
    @staticmethod
    def get_routes():
        return get_full_route_map()


@api_view(["GET"])
@never_cache
def full_route_map(request):
    routes = get_full_route_map()
    return Response({"routes": routes})


@api_view(["GET"])
def template_health_summary(request):
    result = subprocess.run(
        ["python", "manage.py", "inspect_template_health", "--include-rag"],
        capture_output=True,
        text=True,
    )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return Response({"error": result.stderr})

    templates = []
    for item in data:
        path = item.get("template_path")
        tracked = (
            subprocess.run(
                ["git", "ls-files", "--error-unmatch", str(path)],
                capture_output=True,
            ).returncode
            == 0
        )
        item["git_tracked"] = tracked
        templates.append(item)

    return Response({"templates": templates})


@api_view(["POST"])
def reload_templates(request):
    from django.template import engines

    for e in engines.all():
        e.engine.template_loaders = None
    return Response({"reloaded": True})


@api_view(["GET"])
def template_detail(request, slug):
    path = Path(slug)
    info = {}
    status_file = Path("logs/template_status.json")
    if status_file.exists():
        all_info = json.loads(status_file.read_text())
        info = all_info.get(str(path), {})
    content = ""
    if path.exists():
        content = path.read_text()
    return Response({"path": str(path), "content": content, "info": info})


@api_view(["GET"])
def template_diff(request, slug):
    path = Path(slug)
    try:
        subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(path)],
            check=True,
            capture_output=True,
        )
        result = subprocess.run(
            ["git", "diff", str(path)], capture_output=True, text=True
        )
        diff_text = result.stdout
        tracked = True
    except subprocess.CalledProcessError:
        diff_text = ""
        tracked = False
    return Response({"path": str(path), "diff": diff_text, "tracked": tracked})


from api.permissions import AdminOnly


@api_view(["GET"])
@permission_classes([AdminOnly])
def export_assistants(request):
    """Return a JSON dump of all assistants."""
    from assistants.models.assistant import Assistant

    assistants = [model_to_dict(a) for a in Assistant.objects.all()]
    return Response({"assistants": assistants})


@api_view(["GET"])
@permission_classes([AdminOnly])
def export_routes(request):
    """Return a JSON dump of all URL routes with view info."""
    routes = get_full_route_map()
    return Response({"routes": routes})


@api_view(["GET"])
@permission_classes([AdminOnly])
def export_templates(request):
    """Return template health info as raw JSON."""
    result = subprocess.run(
        ["python", "manage.py", "inspect_template_health", "--include-rag"],
        capture_output=True,
        text=True,
    )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return Response({"error": result.stderr})
    return Response({"templates": data})


@api_view(["GET"])
@permission_classes([AllowAny])
def auth_debug(request):
    return Response(
        {
            "authenticated": request.user.is_authenticated,
            "user": request.user.username if request.user.is_authenticated else None,
            "session_keys": list(request.session.keys()),
            "cookies": {k: request.COOKIES.get(k) for k in ["access", "refresh"] if k in request.COOKIES},
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def assistant_routing_debug(request):
    """Return onboarding status and primary assistant slug."""

    if not request.user.is_authenticated:
        return Response({"onboarding_complete": False, "primary_slug": None})

    return Response(
        {
            "onboarding_complete": bool(getattr(request.user, "onboarding_complete", False)),
            "primary_slug": getattr(request.user, "primary_assistant_slug", None),
        }
    )
