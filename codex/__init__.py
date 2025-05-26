from importlib import import_module

# Re-export everything from backend.codex
module = import_module("backend.codex")
for attr in getattr(module, "__all__", []):
    globals()[attr] = getattr(module, attr)

# Fallback: expose module contents to maintain backwards compatibility
for _k, _v in module.__dict__.items():
    if not _k.startswith("_"):
        globals().setdefault(_k, _v)
