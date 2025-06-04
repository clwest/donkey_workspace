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
}
