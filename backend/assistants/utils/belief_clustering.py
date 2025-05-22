from collections import defaultdict

from assistants.models.assistant import Assistant


def cluster_assistant_beliefs() -> list[dict]:
    """Group assistants by ideological attributes and tone."""

    groups = defaultdict(list)
    for a in Assistant.objects.all():
        ideology = a.ideology or {}
        alignment = ideology.get("alignment", "unknown")
        key = (
            alignment,
            a.tone or "",
            tuple(sorted(a.values or [])),
        )
        groups[key].append(a)

    result = []
    for (alignment, tone, values), assistants in groups.items():
        result.append(
            {
                "alignment": alignment,
                "tone": tone,
                "values": list(values),
                "assistants": [a.slug for a in assistants],
            }
        )
    return result
