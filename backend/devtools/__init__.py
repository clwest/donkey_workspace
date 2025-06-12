"""Devtools package initialization."""

# Expose the Django app configuration
default_app_config = "devtools.apps.DevtoolsConfig"

# Lazy attribute access to avoid loading Django views before the app registry
_exported_names = {
    "full_route_map",
    "export_assistants",
    "export_routes",
    "export_templates",
    "auth_debug",
    "assistant_routing_debug",
}


def __getattr__(name):
    if name in _exported_names:
        from . import views

        return getattr(views, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name}")


__all__ = sorted(_exported_names)
