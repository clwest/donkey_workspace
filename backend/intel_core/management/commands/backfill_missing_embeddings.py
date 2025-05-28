from django.core.management.base import BaseCommand
from intel_core.models import DocumentChunk
from embeddings.tasks import embed_and_store


class Command(BaseCommand):
    """Queue embedding tasks for all chunks missing embeddings."""

    help = "Backfill embedding for all unembedded document chunks."

    def handle(self, *args, **kwargs):
        chunks = DocumentChunk.objects.filter(embedding__isnull=True)
        print(f"🔍 Found {chunks.count()} chunks missing embeddings.")
        for chunk in chunks:
            preview = chunk.text[:60].replace("\n", " ")
            print(f"📌 Embedding chunk {chunk.id} ({preview})")
            embed_and_store.delay(str(chunk.id))
