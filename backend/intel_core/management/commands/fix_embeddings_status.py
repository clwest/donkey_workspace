from django.core.management.base import BaseCommand
from intel_core.models import DocumentChunk


class Command(BaseCommand):
    """Fix stale embedding_status values for chunks with embeddings."""

    help = "Set embedding_status='embedded' on chunks that already have embeddings"

    def handle(self, *args, **options):
        qs = DocumentChunk.objects.filter(embedding__isnull=False).exclude(
            embedding_status="embedded"
        )
        count = qs.count()
        qs.update(embedding_status="embedded")
        self.stdout.write(self.style.SUCCESS(f"Updated {count} chunks"))

