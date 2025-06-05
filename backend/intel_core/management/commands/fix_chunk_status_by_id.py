from django.core.management.base import BaseCommand
from intel_core.models import DocumentChunk


class Command(BaseCommand):
    """Fix stale status for a specific DocumentChunk."""

    help = "Set embedding_status='embedded' on the given chunk if a vector exists"

    def add_arguments(self, parser):
        parser.add_argument("--id", type=int, required=True)

    def handle(self, *args, **options):
        chunk_id = options["id"]
        try:
            chunk = DocumentChunk.objects.select_related("embedding").get(pk=chunk_id)
        except DocumentChunk.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Chunk {chunk_id} not found"))
            return

        if chunk.embedding_status == DocumentChunk.EmbeddingStatus.EMBEDDED:
            self.stdout.write(self.style.WARNING(f"Chunk {chunk_id} already marked as 'embedded'"))
            return

        if not chunk.embedding or not getattr(chunk.embedding, "vector", None):
            self.stderr.write(self.style.WARNING(f"Chunk {chunk_id} missing embedding vector"))
            return

        chunk.embedding_status = DocumentChunk.EmbeddingStatus.EMBEDDED
        chunk.save(update_fields=["embedding_status"])
        self.stdout.write(self.style.SUCCESS(f"\u2705 Chunk {chunk_id}: Status updated to 'embedded'"))