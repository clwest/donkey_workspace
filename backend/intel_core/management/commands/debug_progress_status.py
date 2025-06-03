from django.core.management.base import BaseCommand
from intel_core.models import Document, DocumentChunk, DocumentProgress


class Command(BaseCommand):
    help = "Display chunk and progress stats for a document"

    def add_arguments(self, parser):
        parser.add_argument("document_id", help="ID of the document to inspect")

    def handle(self, *args, **options):
        doc_id = options["document_id"]
        document = Document.objects.filter(id=doc_id).first()
        if not document:
            self.stdout.write(self.style.ERROR(f"No document found with id {doc_id}"))
            return

        chunk_total = DocumentChunk.objects.filter(document=document).count()
        embedded_total = DocumentChunk.objects.filter(
            document=document, embedding__isnull=False
        ).count()

        progress = None
        progress_id = None
        if isinstance(document.metadata, dict):
            progress_id = document.metadata.get("progress_id")
            if progress_id:
                progress = DocumentProgress.objects.filter(
                    progress_id=progress_id
                ).first()

        self.stdout.write(f"Chunks embedded: {embedded_total} / {chunk_total}")
        if progress:
            self.stdout.write(
                f"DocumentProgress processed: {progress.processed}/{progress.total_chunks}\n"
                f"DocumentProgress embedded: {progress.embedded_chunks}/{progress.total_chunks}\n"
                f"Status: {progress.status}"
            )
            mismatch = False
            if (
                progress.total_chunks != chunk_total
                or progress.embedded_chunks != embedded_total
            ):
                mismatch = True
            if mismatch:
                self.stdout.write(self.style.WARNING("⚠️ Counts mismatch"))
        else:
            self.stdout.write("No DocumentProgress record found")
