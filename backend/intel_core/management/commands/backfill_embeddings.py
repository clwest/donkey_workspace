from django.core.management.base import BaseCommand
from intel_core.models import DocumentChunk, EmbeddingMetadata
from embeddings.helpers import generate_embedding
from prompts.utils.token_helpers import EMBEDDING_MODEL


class Command(BaseCommand):
    """Generate embeddings for chunks that lack them."""

    help = "Backfill embeddings for document chunks without embeddings."

    def handle(self, *args, **kwargs):
        chunks = DocumentChunk.objects.filter(embedding__isnull=True)
        for chunk in chunks:
            vector = generate_embedding(chunk.text)
            if vector is None:
                self.stdout.write(
                    self.style.WARNING(
                        f"Failed to generate embedding for chunk {chunk.id}"
                    )
                )
                continue

            if hasattr(vector, "tolist"):
                vector = vector.tolist()

            metadata = EmbeddingMetadata.objects.create(
                model_used=EMBEDDING_MODEL,
                num_tokens=chunk.tokens,
                vector=vector,
                status="completed",
                source="backfill",
            )

            chunk.embedding = metadata
            chunk.save(update_fields=["embedding"])

            self.stdout.write(
                self.style.SUCCESS(
                    f"Embedded chunk {chunk.id} of document {chunk.document_id}"
                )
            )
