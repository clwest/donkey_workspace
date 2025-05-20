from typing import Any, Callable, Dict

from assistants.models import Assistant
from agents.models import Agent

from tools.models import Tool, ToolUsageLog, ToolScore

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
        input_data=input_data,
        output_data=output,
        status=status,
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
