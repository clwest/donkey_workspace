CAPABILITY_REGISTRY = {
    "can_train_glossary": {
        "route": "/api/prompts/glossary/",
        "description": "Allow assistant to train glossary terms",
    },
    "can_run_reflection": {
        "route": "/api/v1/assistants/reflect/",
        "description": "Enable reflection cycle endpoints",
    },
    "can_delegate_tasks": {
        "route": "/api/assistants/delegate/",
        "description": "Allow task delegation",
    },
    "can_ingest_docs": {
        "route": "/api/intel/ingest/",
        "description": "Permit document ingestion",
    },
    "can_embed": {
        "route": "/api/embeddings/",
        "description": "Enable embedding API usage",
    },
    "can_self_fork": {
        "route": "/api/assistants/fork/",
        "description": "Allow assistant self-forking",
    },
    "can_reflect_on_self": {
        "route": "/api/assistants/reflect_on_self/",
        "description": "Allow self-reflection endpoint",
    },
    "can_summarize_delegations": {
        "route": "/api/assistants/summarize_delegations/",
        "description": "Summarize delegation memories",
    },
    "can_subagent_reflect": {
        "route": "/api/assistants/subagent_reflect/",
        "description": "Reflect on subagent output",
    },
}


def get_capability_for_path(path: str):
    """Return capability key if the given API path matches a registered route."""
    for key, info in CAPABILITY_REGISTRY.items():
        route = info.get("route", "").lstrip("/")
        if not route:
            continue
        if path.startswith(route):
            return key
    return None


def get_capabilities():
    return CAPABILITY_REGISTRY


__all__ = ["CAPABILITY_REGISTRY", "get_capabilities", "get_capability_for_path"]
