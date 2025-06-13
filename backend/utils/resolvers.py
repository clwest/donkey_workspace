from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from .uuid_utils import is_valid_uuid


def resolve_or_error(value: str, model, slug_field: str = "slug"):
    """Resolve model instance by slug or UUID, raising ``ObjectDoesNotExist``."""
    if not value:
        raise ObjectDoesNotExist(f"No identifier provided for {model.__name__}")

    filters = Q(**{slug_field: value})
    if is_valid_uuid(value):
        filters |= Q(id=value)

    qs = model.objects.filter(filters)
    if not qs.exists():
        raise ObjectDoesNotExist(f"{model.__name__} not found for identifier '{value}'")
    if qs.count() > 1:
        # pick the first but warn about ambiguity
        print(
            f"⚠️ Multiple {model.__name__} objects match '{value}'. Using {qs.first().pk}."
        )
    return qs.first()
