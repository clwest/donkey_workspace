from django.utils import timezone
from django.utils.text import slugify

from agents.models import LoreEntry, SwarmMemoryEntry
from mcp_core.models import Tag


def harmonize_global_narrative() -> dict:
    """Analyze lore conflicts and propose harmonization suggestions."""

    total = LoreEntry.objects.count()
    canon = LoreEntry.objects.filter(is_canon=True).count()
    conflicts = total - canon

    alignment_score = canon / float(total or 1)
    summary = (
        f"lore: {total}; canon: {canon}; conflicts: {conflicts};"
        f" alignment {alignment_score:.2f}"
    )

    entry = SwarmMemoryEntry.objects.create(
        title="Global Narrative Harmonization",
        content=summary,
        origin="narrative_sync",
    )

    for name in ["narrative_sync", "harmonization", "myth_consolidation"]:
        tag, _ = Tag.objects.get_or_create(name=name, defaults={"slug": slugify(name)})
        entry.tags.add(tag)

    return {
        "alignment_score": round(alignment_score, 2),
        "summary": summary,
        "entry_id": entry.id,
    }
