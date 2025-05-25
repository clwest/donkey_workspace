"""Utilities for detecting narrative role collisions across assistants."""

from assistants.models.assistant import Assistant


def detect_role_collisions() -> list[dict]:
    """Identify conflicting roles based on shared memory tags."""
    assistants = Assistant.objects.prefetch_related("memories__tags").all()

    tag_map: dict[str, set[str]] = {}
    for assistant in assistants:
        tags = set()
        for mem in assistant.memories.all():
            tags.update(t.slug for t in mem.tags.all())
        tag_map[str(assistant.id)] = tags

    collisions: list[dict] = []
    ass_list = list(assistants)
    for i, a in enumerate(ass_list):
        for b in ass_list[i + 1 :]:
            overlap = tag_map[str(a.id)].intersection(tag_map[str(b.id)])
            if not overlap:
                continue

            conflict_type = "archetype" if a.archetype_path != b.archetype_path else "memory"
            tension_score = len(overlap)
            collisions.append(
                {
                    "assistant_a": str(a.id),
                    "assistant_b": str(b.id),
                    "conflict_type": conflict_type,
                    "shared_memory": sorted(overlap),
                    "tension_score": tension_score,
                    "proposed_resolution": (
                        "clarify archetypes" if conflict_type == "archetype" else "merge memories"
                    ),
                }
            )

    return collisions
