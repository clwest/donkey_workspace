import logging
from django.apps import apps
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def reflect_on_project_memory(project_id: str) -> str | None:
    """Run reflection when project memory links change."""
    Project = apps.get_model("project", "Project")
    MemoryContext = apps.get_model("mcp_core", "MemoryContext")
    engine_cls = apps.get_app_config("assistants").module.utils.assistant_reflection_engine.AssistantReflectionEngine
    project = Project.objects.filter(id=project_id).select_related("assistant").first()
    if not project or not project.assistant:
        logger.warning("Project %s missing assistant", project_id)
        return None
    context = MemoryContext.objects.create(target=project, content=f"Reflection for project {project.title}")
    engine = engine_cls(project.assistant)
    engine.reflect_now(context)
    return str(context.id)


@shared_task
def auto_tag_new_memory(memory_id: str) -> str | None:
    """Compute embedding and tags for a MemoryEntry."""
    MemoryEntry = apps.get_model("memory", "MemoryEntry")
    Tag = apps.get_model("mcp_core", "Tag")
    save_embedding = apps.get_app_config("embeddings").module.helpers.helpers_io.save_embedding
    auto_tag = apps.get_app_config("mcp_core").module.utils.auto_tag_from_embedding.auto_tag_from_embedding
    memory = MemoryEntry.objects.filter(id=memory_id).first()
    if not memory:
        return None
    text = memory.summary or memory.event
    try:
        embedding = apps.get_app_config("embeddings").module.helpers.helpers_processing.generate_embedding(text)
        if embedding:
            save_embedding(memory, embedding)
    except Exception as e:
        logger.error("Embedding failed: %s", e)
    try:
        slugs = auto_tag(text) or []
        tags = []
        for slug in slugs:
            tag, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": slug})
            tags.append(tag)
        if tags:
            memory.tags.add(*tags)
            memory.auto_tagged = True
            memory.save(update_fields=["auto_tagged"])
    except Exception as e:
        logger.error("Auto tag failed: %s", e)
    return str(memory.id)


@shared_task
def bootstrap_assistant_from_doc(doc_id: str) -> str | None:
    """Create a draft Assistant from a Document."""
    Document = apps.get_model("intel_core", "Document")
    Prompt = apps.get_model("prompts", "Prompt")
    Assistant = apps.get_model("assistants", "Assistant")
    doc = Document.objects.filter(id=doc_id).first()
    if not doc:
        return None
    prompt = Prompt.objects.create(title=f"Summary of {doc.title}", content=doc.summary or doc.content[:200])
    assistant = Assistant.objects.create(name=f"Draft {doc.title}", specialty="bootstrap", system_prompt=prompt)
    return str(assistant.id)


@shared_task
def fragment_codex_clause(clause_id: str) -> str | None:
    """Split a codex clause into fragments."""
    try:
        Clause = apps.get_model("agents", "CodexClause")
        Fragment = apps.get_model("agents", "CodexClauseFragment")
    except LookupError:
        logger.warning("Codex models not available")
        return None
    clause = Clause.objects.filter(id=clause_id).first()
    if not clause:
        return None
    text = clause.text or ""
    parts = [p.strip() for p in text.split(".") if p.strip()]
    created = []
    for part in parts:
        frag = Fragment.objects.create(clause=clause, text=part)
        created.append(frag.id)
    return ",".join(str(i) for i in created)


@shared_task
def decompose_ritual(ritual_id: str) -> str | None:
    """Generate a decomposition plan for a ritual."""
    try:
        Ritual = apps.get_model("agents", "RitualArchiveEntry")
        Plan = apps.get_model("agents", "RitualDecompositionPlan")
        Step = apps.get_model("agents", "DecomposedStepTrace")
    except LookupError:
        logger.warning("Ritual models not available")
        return None
    ritual = Ritual.objects.filter(id=ritual_id).first()
    if not ritual:
        return None
    plan = Plan.objects.create(ritual=ritual, summary=f"Decomposition of {ritual.name}")
    Step.objects.create(plan=plan, step_text=ritual.symbolic_impact_summary)
    return str(plan.id)


@shared_task
def mine_swarm_codification_patterns() -> int:
    """Analyze logs and create codex expansion suggestions."""
    try:
        Pattern = apps.get_model("agents", "SwarmCodificationPattern")
        Suggestion = apps.get_model("agents", "CodexExpansionSuggestion")
    except LookupError:
        logger.warning("Codex pattern models not available")
        return 0
    count = 0
    for pattern in Pattern.objects.all():
        Suggestion.objects.get_or_create(pattern=pattern, defaults={"summary": pattern.summary})
        count += 1
    return count
