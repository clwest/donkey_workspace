from django.core.management.base import BaseCommand
from intel_core.models import Document, DocumentChunk, DocumentProgress


class Command(BaseCommand):
    """Recount chunks and embeddings, update progress status."""

    help = "Reconcile DocumentProgress counts for a document"

    def add_arguments(self, parser):
        parser.add_argument("--doc-id", dest="doc_id", required=True)
        parser.add_argument("--repair", action="store_true", help="Force repair progress record and chunk states")

    def handle(self, *args, **options):
        doc_id = options["doc_id"]
        repair = options.get("repair")

        document = Document.objects.filter(id=doc_id).first()
        if not document:
            self.stderr.write(f"Document {doc_id} not found")
            return

        chunks = DocumentChunk.objects.filter(document=document).order_by("order")
        chunk_total = chunks.count()

        progress_id = None
        if isinstance(document.metadata, dict):
            progress_id = document.metadata.get("progress_id")

        progress = None
        if progress_id:
            progress = DocumentProgress.objects.filter(progress_id=progress_id).first()

        summary_marked = 0
        summary_orphaned = 0

        if repair:
            for ch in chunks:
                meta = ch.embedding
                meta_status = getattr(meta, "status", None)
                has_emb = getattr(meta, "embedding_id", None)
                if has_emb and meta_status == "completed" and ch.embedding_status != "embedded":
                    ch.embedding_status = "embedded"
                    ch.save(update_fields=["embedding_status"])
                    summary_marked += 1
                elif not has_emb and ch.embedding_status == "embedded":
                    ch.embedding_status = "pending"
                    ch.save(update_fields=["embedding_status"])
                    summary_orphaned += 1

        embedded_total = chunks.filter(embedding_status="embedded").count()
        failed_list = list(
            chunks.filter(embedding_status="failed").values_list("order", flat=True)
        )

        if not progress and repair:
            progress = DocumentProgress.objects.create(
                title=document.title,
                total_chunks=chunk_total,
                processed=chunk_total,
                embedded_chunks=embedded_total,
                status="pending",
            )
            document.metadata = document.metadata or {}
            document.metadata["progress_id"] = str(progress.progress_id)
            document.save(update_fields=["metadata"])
        elif not progress:
            self.stderr.write("No DocumentProgress record found")
            return

        progress.total_chunks = chunk_total
        progress.processed = max(progress.processed, chunk_total)
        progress.embedded_chunks = embedded_total
        progress.failed_chunks = failed_list
        if failed_list:
            progress.status = "failed"
        elif (
            progress.status != "failed"
            and progress.total_chunks > 0
            and progress.embedded_chunks >= progress.total_chunks
        ):
            progress.status = "completed"
        progress.save()

        msg = (
            f"Progress {progress.progress_id} -> {progress.embedded_chunks}/{progress.total_chunks} ({progress.status})"
        )
        if repair:
            msg += f" | Marked {summary_marked} chunk(s) as embedded, repaired {summary_orphaned} orphaned chunk(s)"
        self.stdout.write(msg)
