from django.core.management.base import BaseCommand
from intel_core.models import Document, DocumentChunk, DocumentProgress


class Command(BaseCommand):
    """Recount chunks and embeddings, update progress status."""

    help = "Reconcile DocumentProgress counts for a document"

    def add_arguments(self, parser):
        parser.add_argument("--doc-id", dest="doc_id", required=True)

    def handle(self, *args, **options):
        doc_id = options["doc_id"]
        document = Document.objects.filter(id=doc_id).first()
        if not document:
            self.stderr.write(f"Document {doc_id} not found")
            return

        chunk_total = DocumentChunk.objects.filter(document=document).count()
        embedded_total = DocumentChunk.objects.filter(
            document=document, embedding__isnull=False
        ).count()
        progress_id = None
        if isinstance(document.metadata, dict):
            progress_id = document.metadata.get("progress_id")
        progress = None
        if progress_id:
            progress = DocumentProgress.objects.filter(progress_id=progress_id).first()
        if not progress:
            self.stderr.write("No DocumentProgress record found")
            return

        progress.total_chunks = chunk_total
        progress.processed = max(progress.processed, chunk_total)
        progress.embedded_chunks = embedded_total
        if (
            progress.status != "failed"
            and progress.total_chunks > 0
            and progress.embedded_chunks >= progress.total_chunks
        ):
            progress.status = "completed"
        progress.save()
        self.stdout.write(
            f"Progress {progress.progress_id} -> {progress.embedded_chunks}/{progress.total_chunks} ({progress.status})"
        )
