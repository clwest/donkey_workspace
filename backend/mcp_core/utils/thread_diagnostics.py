from datetime import timedelta
from collections import Counter
from django.utils import timezone
from assistants.models import AssistantThoughtLog
from memory.models import MemoryEntry
from mcp_core.models import NarrativeThread, ThreadDiagnosticLog


def run_thread_diagnostics(thread: NarrativeThread) -> dict:
    now = timezone.now()
    last_memory = (
        MemoryEntry.objects.filter(thread=thread)
        .order_by("-created_at")
        .first()
    )
    last_thought = (
        AssistantThoughtLog.objects.filter(narrative_thread=thread)
        .order_by("-created_at")
        .first()
    )

    days_since_memory = (
        (now - last_memory.created_at).days if last_memory else None
    )
    days_since_thought = (
        (now - last_thought.created_at).days if last_thought else None
    )

    assistant_count = (
        AssistantThoughtLog.objects.filter(narrative_thread=thread)
        .values_list("assistant_id", flat=True)
        .distinct()
        .count()
    )

    memories = MemoryEntry.objects.filter(thread=thread)
    project_ratio = 0.0
    if memories.exists():
        project_ratio = (
            memories.filter(related_project__isnull=False).count() / memories.count()
        )

    score = 1.0
    if days_since_memory is None:
        score -= 0.3
    elif days_since_memory > 30:
        score -= 0.4
    elif days_since_memory > 7:
        score -= 0.2

    if days_since_thought is None:
        score -= 0.2
    elif days_since_thought > 30:
        score -= 0.3
    elif days_since_thought > 7:
        score -= 0.1

    if assistant_count == 0:
        score -= 0.2
    elif assistant_count == 1:
        score -= 0.05

    score += 0.2 * project_ratio
    score = max(0.0, min(score, 1.0))

    parts = []
    if days_since_memory is not None:
        parts.append(f"last memory {days_since_memory}d ago")
    else:
        parts.append("no memories")
    if days_since_thought is not None:
        parts.append(f"last thought {days_since_thought}d ago")
    else:
        parts.append("no thoughts")
    parts.append(f"{assistant_count} assistants")
    parts.append(f"{int(project_ratio * 100)}% memories linked to projects")
    summary = ", ".join(parts)

    moods = list(
        AssistantThoughtLog.objects.filter(narrative_thread=thread)
        .order_by("created_at")
        .values_list("mood", flat=True)
    )
    mood_counts = Counter(moods)
    avg_mood = mood_counts.most_common(1)[0][0] if mood_counts else None
    volatility = sum(1 for i in range(1, len(moods)) if moods[i] != moods[i - 1])

    mood_influence = ""
    if avg_mood:
        thread.avg_mood = avg_mood
        if score < 0.6 and avg_mood in {"anxious", "frustrated"}:
            mood_influence = f"Low mood ({avg_mood}) may impact planning"
        elif volatility > 3:
            mood_influence = "Mood volatility detected"

    ThreadDiagnosticLog.objects.create(
        thread=thread, score=score, summary=summary, mood_influence=mood_influence
    )
    thread.continuity_score = score
    thread.last_diagnostic_run = now
    thread.save(update_fields=["continuity_score", "last_diagnostic_run", "avg_mood"])

    return {"score": score, "summary": summary}
