from django.db.models import Q
from assistants.models import Assistant


def resolve_assistant(value: str):
    """Return Assistant by UUID or slug, printing warnings if ambiguous."""
    qs = Assistant.objects.filter(Q(id=value) | Q(slug=value))
    if not qs.exists():
        return None
    if qs.count() > 1:
        print(
            f"⚠️ Multiple assistants match '{value}'. Using {qs.first().slug} ({qs.first().id})."
        )
    return qs.first()
