from django.core.management.base import BaseCommand
from intel_core.models import DocumentChunk
from intel_core.utils.processing import compute_glossary_score
from embeddings.tasks import embed_and_store


class Command(BaseCommand):
    """Re-embed and re-index a specific DocumentChunk."""

    help = "Re-embed a single DocumentChunk by primary key"

    def add_arguments(self, parser):
        parser.add_argument("--id", type=int, required=True)

    def handle(self, *args, **options):
        chunk_id = options["id"]
        try:
            chunk = DocumentChunk.objects.get(pk=chunk_id)
        except DocumentChunk.DoesNotExist:
            self.stderr.write(f"Chunk {chunk_id} not found")
            return

        self.stdout.write(f"\U0001F4E6 Re-embedding chunk {chunk_id}...")
        chunk.embedding = None
        chunk.embedding_status = DocumentChunk.EmbeddingStatus.PENDING
        score, matched = compute_glossary_score(chunk.text)
        chunk.glossary_score = score
        if matched:
            chunk.matched_anchors = matched
        chunk.save(
            update_fields=[
                "embedding",
                "embedding_status",
                "glossary_score",
                "matched_anchors",
            ]
        )
        embed_and_store.delay(str(chunk.id))
        self.stdout.write(self.style.SUCCESS("Embedding task queued."))
