from django.core.management.base import BaseCommand
from intel_core.models import Document, DocumentChunk


class Command(BaseCommand):
    """Verify embedding integrity for a document."""

    help = "Check that all chunks for a document have valid embeddings"

    def add_arguments(self, parser):
        parser.add_argument("doc_id", help="Document ID to verify")

    def handle(self, *args, **options):
        doc_id = options["doc_id"]
        try:
            document = Document.objects.get(id=doc_id)
        except Document.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Document {doc_id} not found"))
            return

        chunks = DocumentChunk.objects.filter(document=document).order_by("order")
        total = chunks.count()
        embedded = 0
        self.stdout.write(f"Verifying {total} chunks for '{document.title}'\n")

        for chunk in chunks:
            prefix = f"Chunk {chunk.order}: "
            if not chunk.embedding:
                self.stdout.write(self.style.ERROR(prefix + "missing embedding"))
                continue
            vector = getattr(chunk.embedding, "vector", None)
            if not vector or len(vector) != 1536:
                self.stdout.write(
                    self.style.WARNING(
                        prefix + f"invalid vector len={len(vector) if vector else 0}"
                    )
                )
                continue
            if not getattr(chunk.embedding, "id", None):
                self.stdout.write(self.style.WARNING(prefix + "missing embedding_id"))
            else:
                self.stdout.write(self.style.SUCCESS(prefix + "ok"))
            embedded += 1

        self.stdout.write(
            f"\nEmbedded {embedded} / {total} chunks verified successfully"
        )
