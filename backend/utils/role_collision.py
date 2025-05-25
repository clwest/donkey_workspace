"""Role collision detection utilities."""

from assistants.models.assistant import Assistant

def detect_role_collisions() -> list[dict]:
    """Compare current assistant archetypes and memory intersections."""
    assistants = Assistant.objects.prefetch_related("memories__tags").all()

    tag_map: dict[str, set[str]] = {}
    for a in assistants:
        tags = set()
        for mem in a.memories.all():
            tags.update(t.slug for t in mem.tags.all())
        tag_map[str(a.id)] = tags

    collisions: list[dict] = []
    ass_list = list(assistants)
    for i, a in enumerate(ass_list):
        for b in ass_list[i + 1 :]:
            overlap = tag_map[str(a.id)].intersection(tag_map[str(b.id)])
            if not overlap:
                continue

            if a.archetype_path != b.archetype_path:
                proposal = "clarify archetypes or split memory responsibilities"
            else:
                proposal = "merge roles or coordinate memory usage"

            collisions.append(
                {
                    "assistant_a": str(a.id),
                    "assistant_b": str(b.id),
                    "shared_tags": sorted(overlap),
                    "proposal": proposal,
                }
            )

    return collisions
