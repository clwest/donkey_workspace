from django.urls import get_resolver
from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
import inspect
from capabilities.registry import get_capability_for_path
import subprocess
import json
from pathlib import Path


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
