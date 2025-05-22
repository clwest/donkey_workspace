from assistants.models.assistant import Assistant


def build_constellation_map() -> dict:
    """Return a simple mapping of assistants grouped by persona mode."""

    clusters = {}
    for assistant in Assistant.objects.all():
        mode = assistant.persona_mode or "default"
        clusters.setdefault(mode, []).append({
            "id": str(assistant.id),
            "name": assistant.name,
            "slug": assistant.slug,
        })

    return {"clusters": clusters}
