from typing import Tuple, List

from memory.models import MemoryEntry


def replay_scene(
    thread_id, assistant=None, limit: int = 5
) -> Tuple[str, List[MemoryEntry]]:
    """Return a formatted replay block and associated memories for a thread."""
    qs = MemoryEntry.objects.filter(thread_id=thread_id)
    if assistant:
        qs = qs.filter(assistant=assistant)
    memories = list(qs.order_by("-importance", "-created_at")[:limit])

    if not memories:
        return "You are revisiting a past scene, but no memories were found.", []

    lines = []
    for m in memories:
        ts = m.timestamp.strftime("%Y-%m-%d %H:%M") if m.timestamp else ""
        summary = m.summary or m.event.split("\n")[0][:80]
        lines.append(f"- [{ts}] {summary}")

    block = (
        "You are revisiting a past scene.\n\n"
        "\U0001f9e0 Past Highlights:\n" + "\n".join(lines)
    )
    return block, memories
