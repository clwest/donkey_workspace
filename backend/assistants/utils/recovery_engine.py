from assistants.models import (
    Assistant,
    AssistantObjective,
    AssistantTask,
    AssistantThoughtLog,
)


def regenerate_assistant_plan(
    assistant: Assistant, recovery_reason: str | None = None
) -> dict:
    """Generate a basic recovery plan summary from recent data."""
    thoughts = list(
        assistant.thoughts.order_by("-created_at").values_list("thought", flat=True)[:5]
    )
    objectives = list(
        AssistantObjective.objects.filter(assistant=assistant)
        .order_by("-created_at")
        .values_list("title", flat=True)[:3]
    )
    tasks = list(
        AssistantTask.objects.filter(project__assistant=assistant)
        .order_by("-created_at")
        .values_list("title", flat=True)[:3]
    )
    drift = list(
        assistant.drift_logs.order_by("-created_at").values_list("summary", flat=True)[
            :2
        ]
    )

    summary_parts = [*drift, *thoughts, *objectives, *tasks]
    summary = "; ".join([p for p in summary_parts if p])

    plan = {
        "milestones": [{"title": f"Review objective: {o}"} for o in objectives]
        or [{"title": "Review recent progress"}],
        "prompt_adjustment": "Focus on core specialty and tighten system prompt.",
    }

    log = AssistantThoughtLog.objects.create(
        assistant=assistant,
        thought=f"Regenerated plan: {summary}",
        thought_type="regeneration",
        category="insight",
        source_reason=recovery_reason,
        event="assistant_plan_regenerated",
    )

    return {"summary": summary, "plan": plan, "thought_id": str(log.id)}
