from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.contrib.contenttypes.models import ContentType

from embeddings.models import Embedding


class Command(BaseCommand):
    """Audit Embedding metadata for missing session_id or source_type."""

    help = "Audit embeddings where session_id or source_type is missing"

    def handle(self, *args, **options):
        qs = Embedding.objects.filter(
            Q(session_id__isnull=True) | Q(source_type__isnull=True)
        )
        total = qs.count()
        missing_session = qs.filter(session_id__isnull=True).count()
        missing_source = qs.filter(source_type__isnull=True).count()

        self.stdout.write(f"Found {total} orphan embeddings:")
        self.stdout.write(f"• {missing_session} missing session_id")
        self.stdout.write(f"• {missing_source} missing source_type")

        breakdown = (
            qs.values("content_type_id").annotate(count=Count("id")).order_by("-count")
        )
        for row in breakdown:
            ct = ContentType.objects.filter(id=row["content_type_id"]).first()
            model = ct.model if ct else "unknown"
            self.stdout.write(f"- {model}: {row['count']}")
