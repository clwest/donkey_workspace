from django.db.models import Q
from assistants.models import Assistant
from utils import is_valid_uuid


def resolve_assistant(value: str):
    """Return Assistant by UUID or slug, printing warnings if ambiguous."""
    if not value:
        return None

    filters = Q(slug=value)
    if is_valid_uuid(value):
        filters |= Q(id=value)

    qs = Assistant.objects.filter(filters)
    if not qs.exists():
        return None
    if qs.count() > 1:
        print(
            f"⚠️ Multiple assistants match '{value}'. Using {qs.first().slug} ({qs.first().id})."
        )
    return qs.first()
