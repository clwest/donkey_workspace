from django.core.management.base import BaseCommand
from intel_core.models import Document, DocumentChunk, DocumentProgress
from embeddings.tasks import embed_and_store


class Command(BaseCommand):
    """Re-embed all chunks for a specific document."""

    help = "Recompute embeddings for every chunk on a document"

    def add_arguments(self, parser):
        parser.add_argument("--doc-id", required=True)

    def handle(self, *args, **options):
        doc_id = options["doc_id"]
        try:
            document = Document.objects.get(id=doc_id)
        except Document.DoesNotExist:
            self.stderr.write(f"Document {doc_id} not found")
            return

        chunks = DocumentChunk.objects.filter(document=document)
        total = chunks.count()
        self.stdout.write(
            f"Re-embedding {total} chunks for '{document.title}'"
        )

        for chunk in chunks:
            chunk.embedding = None
            chunk.embedding_status = "pending"
            chunk.save(update_fields=["embedding", "embedding_status"])
            embed_and_store.delay(str(chunk.id))

        progress, _ = DocumentProgress.objects.get_or_create(
            document=document,
            defaults={
                "title": document.title,
                "total_chunks": total,
                "processed": 0,
                "embedded_chunks": 0,
                "failed_chunks": [],
                "status": "in_progress",
            },
        )
        progress.processed = 0
        progress.embedded_chunks = 0
        progress.failed_chunks = []
        progress.status = "in_progress"
        progress.save(
            update_fields=["processed", "embedded_chunks", "failed_chunks", "status"]
        )

        meta = document.metadata or {}
        meta["embedded_chunks"] = 0
        document.metadata = meta
        document.save(update_fields=["metadata"])

        self.stdout.write(self.style.SUCCESS("Embedding tasks queued."))
