from typing import Any, Callable, Dict, Optional, List
from .tool_registry import register_tool


def tool(
    name: str,
    slug: Optional[str] = None,
    *,
    input_schema: Optional[Dict[str, Any]] = None,
    output_schema: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
    description: str | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to mark a function as a tool and auto-register it."""

    def wrapper(fn: Callable[..., Any]) -> Callable[..., Any]:
        reg_slug = slug or fn.__name__
        register_tool(name, reg_slug, None, fn,
                      input_schema=input_schema,
                      output_schema=output_schema,
                      tags=tags or [],
                      description=description or fn.__doc__ or "")
        fn._tool_meta = {
            "name": name,
            "slug": reg_slug,
            "module_path": fn.__module__,
            "function_name": fn.__name__,
            "input_schema": input_schema or {},
            "output_schema": output_schema or {},
            "tags": tags or [],
            "description": description or fn.__doc__ or "",
        }
        return fn

    return wrapper
