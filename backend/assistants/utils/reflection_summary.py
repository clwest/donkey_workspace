from django.utils.text import slugify
from .assistant_reflection_engine import AssistantReflectionEngine
from django.utils import timezone
from assistants.models.reflection import AssistantReflectionLog, ReflectionGroup


def summarize_reflections_for_document(
    document_id=None, assistant_id=None, group_slug=None
):
    qs = AssistantReflectionLog.objects.all()
    if group_slug:
        group = ReflectionGroup.objects.filter(slug=group_slug).first()
        if group:
            qs = group.reflections.all()
    if document_id:
        qs = qs.filter(document_id=document_id)
    if assistant_id:
        qs = qs.filter(assistant_id=assistant_id)
    qs = qs.order_by("created_at")
    if not qs.exists():
        return None

    grouped = {}
    for r in qs:
        key = r.group_slug or slugify(r.title or "group")
        grouped.setdefault(key, []).append(r.summary)

    summary_lines = [f"{k}: {len(v)} reflections" for k, v in grouped.items()]
    summary_text = "; ".join(summary_lines)

    if group_slug and group:
        group.summary = summary_text
        group.summary_updated = timezone.now()
        group.save(update_fields=["summary", "summary_updated"])
        return group

    log = AssistantReflectionLog.objects.create(
        assistant=qs.first().assistant,
        document_id=document_id,
        title="Reflection Summary",
        summary=summary_text,
        group_slug="summary",
        is_summary=True,
    )
    return log
