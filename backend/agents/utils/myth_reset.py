from django.utils import timezone

from agents.models import SwarmMemoryEntry
from .seasonal import get_current_season


def run_myth_reset_cycle() -> dict:
    """Retire collapsed myth layers and suggest new narrative seeds."""
    now = timezone.now()
    season = get_current_season()
    retired = list(
        SwarmMemoryEntry.objects.filter(origin="myth_layer", season=season)
        .order_by("-created_at")[:5]
        .values_list("id", "title")
    )
    entry = SwarmMemoryEntry.objects.create(
        title="Seasonal Myth Reset", content="Myth layers reset", origin="myth_reset"
    )
    try:
        from mcp_core.models import Tag

        for slug in ["myth_reset", "epoch_shift", "ritual_reboot"]:
            tag, _ = Tag.objects.get_or_create(name=slug, defaults={"slug": slug})
            entry.tags.add(tag)
    except Exception:
        pass

    new_seed = {
        "title": f"Dream Seed {now.date()}",
        "details": "Placeholder seed from dream simulation",
    }
    return {"retired": retired, "new_seed": new_seed, "memory_entry": entry.id}
