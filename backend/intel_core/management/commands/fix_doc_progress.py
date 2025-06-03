from django.core.management.base import BaseCommand
from intel_core.models import Document, DocumentChunk, DocumentProgress, EmbeddingMetadata

from uuid import UUID

class Command(BaseCommand):
    help = "Repair or create DocumentProgress records for documents"

    def add_arguments(self, parser):
        parser.add_argument('--doc-id', type=str, help='Document UUID to repair')
        parser.add_argument('--all', action='store_true', help='Repair all documents')
        parser.add_argument('--repair', action='store_true', help='Enable repair mode')

    def handle(self, *args, **options):
        if options['all']:
            docs = Document.objects.all()
        elif options['doc_id']:
            try:
                docs = [Document.objects.get(id=UUID(options['doc_id']))]
            except Document.DoesNotExist:
                self.stdout.write(self.style.ERROR("❌ Document not found."))
                return
        else:
            self.stdout.write(self.style.ERROR("❌ Must provide --doc-id or --all"))
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

            if not created and options['repair']:
                progress.total_chunks = total
                progress.processed = total
                progress.embedded_chunks = embedded
                progress.failed_chunks = list(
                    chunks.filter(embedding_status='failed').values_list('order', flat=True)
                )
                progress.status = 'completed' if embedded == total else 'failed'
                progress.save()
                self.stdout.write(f"🔧 Repaired: {doc.title} -> {embedded}/{total} embedded")
            else:
                self.stdout.write(f"✅ Verified: {doc.title} -> {embedded}/{total} embedded")