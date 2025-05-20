from typing import Any, Callable, Dict

from assistants.models import Assistant
from agents.models import Agent

from tools.models import Tool, ToolUsageLog

_registry: Dict[str, Callable[[Dict[str, Any]], Any]] = {}


def register_tool(
    name: str,
    slug: str,
    schema: Dict[str, Any] | None,
    fn: Callable[[Dict[str, Any]], Any],
) -> None:
    """Register a tool and ensure a matching DB entry exists."""

    _registry[slug] = fn
    Tool.objects.get_or_create(
        slug=slug,
        defaults={"name": name, "description": name, "schema": schema or {}},
    )


def call_tool(slug: str, input_data: Dict[str, Any], caller: Any) -> Any:
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
    ToolUsageLog.objects.create(
        tool=tool,
        assistant=caller if isinstance(caller, Assistant) else None,
        agent=caller if isinstance(caller, Agent) else None,
        input_data=input_data,
        output_data=output,
        status=status,
    )
    return output
