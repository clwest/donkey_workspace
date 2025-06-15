import logging
from typing import List, Optional
from django.utils.text import slugify
from assistants.models.thoughts import AssistantThoughtLog
from assistants.models.project import AssistantProject
from tools.models import Tool
from mcp_core.models import NarrativeThread, Tag
from project.models import Project

logger = logging.getLogger(__name__)


def get_or_create_tool(slug: str) -> Tool:
    """Fetch or create a minimal Tool entry for internal logging."""
    tool, _ = Tool.objects.get_or_create(
        slug=slug,
        defaults={"name": slug.replace('_', ' ').title(), "module_path": "internal", "function_name": slug},
    )
    return tool


def get_or_create_symbolic_thread(assistant, category: str) -> NarrativeThread:
    """Return a narrative thread for symbolic logging."""
    title = f"{assistant.slug}-{category}-thread"
    thread, _ = NarrativeThread.objects.get_or_create(title=title)
    tag, _ = Tag.objects.get_or_create(slug="symbolic", defaults={"name": "symbolic"})
    thread.tags.add(tag)
    return thread


def log_symbolic_thought(
    assistant,
    *,
    category: str = "other",
    thought: str = "",
    thought_type: str = "generated",
    project=None,
    tool_name: Optional[str] = None,
    tool_result_summary: Optional[str] = None,
    summoned_memory_ids: Optional[List[str]] = None,
    fallback_reason: Optional[str] = None,
    fallback_details: Optional[dict] = None,
    origin: str = "auto",
    tags: Optional[List[str]] = None,
    thought_trace: str = "",
    coherence_score: Optional[float] = None,
    integrity_status: Optional[str] = None,
    narrative_thread: Optional[NarrativeThread] = None,
) -> AssistantThoughtLog:
    """Create a structured AssistantThoughtLog entry."""
    if narrative_thread is None:
        narrative_thread = get_or_create_symbolic_thread(assistant, category)

    tool = get_or_create_tool(tool_name) if tool_name else None

    core_project = project
    if isinstance(project, AssistantProject):
        core_project = (
            project.linked_projects.first()
            or Project.objects.filter(assistant_project=project).first()
        )

    log = AssistantThoughtLog.objects.create(
        assistant=assistant,
        project=core_project,
        narrative_thread=narrative_thread,
        category=category,
        thought=thought,
        thought_type=thought_type,
        tool_used=tool,
        tool_result_summary=tool_result_summary,
        summoned_memory_ids=summoned_memory_ids or [],
        fallback_reason=fallback_reason,
        fallback_details=fallback_details,
        origin=origin,
        thought_trace=thought_trace,
        coherence_score=coherence_score,
        integrity_status=integrity_status,
    )

    if tags:
        tag_objs = []
        for name in tags:
            slug = slugify(name)
            t, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": name})
            tag_objs.append(t)
        if tag_objs:
            log.tags.set(tag_objs)
    return log
