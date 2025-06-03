from django.core.management.base import BaseCommand
from django.db.models import F
from intel_core.models import Document, DocumentChunk, DocumentProgress


class Command(BaseCommand):
    """Validate DocumentProgress and chunk embedding status."""

    help = "Check embedding status and counts for a document"

    def add_arguments(self, parser):
        parser.add_argument("--doc-id", dest="doc_id", required=True)

    def handle(self, *args, **options):
        doc_id = options["doc_id"]
        document = Document.objects.filter(id=doc_id).first()
        if not document:
            self.stderr.write(self.style.ERROR(f"Document {doc_id} not found"))
            return

        chunks = DocumentChunk.objects.filter(document=document).order_by("order")
        total = chunks.count()
        embedded_total = chunks.filter(embedding_status="embedded").count()

        progress = None
        progress_id = None
        if isinstance(document.metadata, dict):
            progress_id = document.metadata.get("progress_id")
            if progress_id:
                progress = DocumentProgress.objects.filter(
                    progress_id=progress_id
                ).first()

        self.stdout.write(f"Chunks: {embedded_total}/{total} embedded")
        if progress:
            self.stdout.write(
                f"Progress embedded: {progress.embedded_chunks}/{progress.total_chunks}"
            )
            if (
                progress.embedded_chunks != embedded_total
                or progress.total_chunks != total
            ):
                self.stdout.write(self.style.WARNING("⚠️ Progress counts mismatch"))
        else:
            self.stdout.write("No DocumentProgress record found")

        mismatches = []
        for ch in chunks:
            emb_id = getattr(ch.embedding, "embedding_id", None)
            if ch.embedding_status == "embedded":
                if not emb_id or ch.score is None:
                    mismatches.append(ch)
            else:
                if emb_id:
                    mismatches.append(ch)
        if mismatches:
            self.stdout.write(
                self.style.WARNING(f"Found {len(mismatches)} mismatched chunks:")
            )
            for ch in mismatches:
                emb_id = getattr(ch.embedding, "embedding_id", None)
                self.stdout.write(
                    f" - Chunk {ch.order} status={ch.embedding_status} embedding_id={emb_id} score={ch.score}"
                )
        else:
            self.stdout.write(self.style.SUCCESS("All chunks consistent"))
