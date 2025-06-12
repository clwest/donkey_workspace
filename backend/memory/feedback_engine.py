from __future__ import annotations

from .models import MemoryFeedback, MemoryMutationLog, MemoryEntry


def apply_mutation(
    feedback: MemoryFeedback, new_content: str, *, applied_by: str = "reflection"
) -> MemoryEntry:
    """Apply a mutation to the linked memory and log the change."""
    memory = feedback.memory
    old_content = memory.summary or memory.event
    if memory.summary:
        memory.summary = new_content
    else:
        memory.event = new_content
    memory.save(update_fields=["summary", "event"])
    MemoryMutationLog.objects.create(
        feedback=feedback,
        assistant=memory.assistant,
        memory=memory,
        old_content=old_content,
        new_content=new_content,
        applied_by=applied_by,
    )
    feedback.status = "accepted"
    feedback.save(update_fields=["status"])
    return memory


def check_auto_suppress(memory: MemoryEntry) -> None:
    """Disable memory if repeated negative feedback or severe flags."""
    negative_count = memory.feedback.filter(rating="negative").count()
    high_flag = memory.flags.filter(severity="high").exists()
    if negative_count >= 2 or high_flag:
        if memory.is_active:
            memory.is_active = False
            memory.save(update_fields=["is_active"])
