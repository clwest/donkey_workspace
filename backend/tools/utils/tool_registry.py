import importlib
from pathlib import Path
from typing import Any, Callable, Dict, Optional, List

from django.apps import apps

from assistants.models.assistant import Assistant
from agents.models.core import Agent

from tools.models import Tool, ToolUsageLog, ToolScore, ToolDiscoveryLog

_registry: Dict[str, Callable[[Dict[str, Any]], Any]] = {}


def register_tool(
    name: str,
    slug: str,
    schema: Optional[Dict[str, Any]],
    fn: Callable[[Dict[str, Any]], Any],
    *,
    input_schema: Optional[Dict[str, Any]] = None,
    output_schema: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
    description: str | None = None,
) -> None:
    """Register a tool and ensure a matching DB entry exists."""

    _registry[slug] = fn
    Tool.objects.update_or_create(
        slug=slug,
        defaults={
            "name": name,
            "description": description or name,
            "schema": schema or {},
            "module_path": fn.__module__,
            "function_name": fn.__name__,
            "input_schema": input_schema or {},
            "output_schema": output_schema or {},
            "tags": tags or [],
        },
    )


def call_tool(
    slug: str, input_data: Dict[str, Any], caller: Any, tags: list[str] | None = None
) -> Any:
    """Execute a registered tool and log the usage."""

    if slug not in _registry:
        raise ValueError(f"Tool '{slug}' is not registered")

    tool = Tool.objects.get(slug=slug)
    fn = _registry[slug]
    status = "success"
    try:
        output = fn(input_data)
    except Exception as exc:  # pragma: no cover - simple exception handling
        status = "error"
        output = {"error": str(exc)}

    tags = tags or []
    ToolUsageLog.objects.create(
        tool=tool,
        assistant=caller if isinstance(caller, Assistant) else None,
        agent=caller if isinstance(caller, Agent) else None,
        input_payload=input_data,
        output_payload=output,
        success=status == "success",
        error="" if status == "success" else output.get("error", ""),
    )

    if isinstance(caller, Assistant):
        delta = 1.0 if status == "success" else -1.0
        score, _ = ToolScore.objects.get_or_create(tool=tool, assistant=caller)
        total = score.score * score.usage_count + delta
        score.usage_count += 1
        score.score = total / score.usage_count
        score.context_tags = score.context_tags + tags
        score.save()

    return output


def get_best_tool_for_context(tags: list[str], assistant: Assistant) -> Tool | None:
    """Return the assistant's highest scoring tool matching given tags."""

    scores = ToolScore.objects.filter(assistant=assistant).order_by("-score")
    if tags:
        scores = scores.filter(context_tags__overlap=tags)
    best = scores.first()
    return best.tool if best else None


def discover_tools(directory: Path) -> None:
    """Import modules and register any decorated tools found."""

    for py in directory.rglob("*.py"):
        rel_module = ".".join(py.relative_to(directory.parent).with_suffix("").parts)
        try:
            module = importlib.import_module(rel_module)
        except Exception as exc:  # pragma: no cover - import failure
            ToolDiscoveryLog.objects.create(
                tool=None,
                path=str(py),
                success=False,
                message=str(exc),
            )
            continue

        for attr in dir(module):
            obj = getattr(module, attr)
            meta = getattr(obj, "_tool_meta", None)
            if meta:
                register_tool(
                    meta["name"],
                    meta["slug"],
                    None,
                    obj,
                    input_schema=meta.get("input_schema"),
                    output_schema=meta.get("output_schema"),
                    tags=meta.get("tags"),
                    description=meta.get("description"),
                )
                tool = Tool.objects.get(slug=meta["slug"])
                ToolDiscoveryLog.objects.create(
                    tool=tool,
                    path=str(py),
                    success=True,
                )

def execute_tool(tool: Tool, payload: dict):
    module = importlib.import_module(tool.module_path)
    func = getattr(module, tool.function_name)
    return func(**payload)
