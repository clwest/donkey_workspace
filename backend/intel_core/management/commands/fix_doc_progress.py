from django.core.management.base import BaseCommand
from intel_core.models import Document, DocumentChunk, DocumentProgress
from uuid import UUID


class Command(BaseCommand):
    help = "Repair or create DocumentProgress records for documents"

    def add_arguments(self, parser):
        parser.add_argument('--doc-id', type=str, help='Document UUID to repair')
        parser.add_argument('--all', action='store_true', help='Repair all documents')
        parser.add_argument('--repair', action='store_true', help='Enable repair mode')

    def handle(self, *args, **options):
        repair = options.get('repair', False)

        if options.get('all'):
            documents = Document.objects.all()
        elif options.get('doc_id'):
            try:
                documents = [Document.objects.get(id=UUID(options['doc_id']))]
            except Document.DoesNotExist:
                self.stdout.write(self.style.ERROR("❌ Document not found."))
                return
        else:
            self.stdout.write(self.style.ERROR("❌ Must provide --doc-id or --all"))
            return

        for document in documents:
            chunks = DocumentChunk.objects.filter(document=document).order_by("order")
            total = chunks.count()

            embedded = 0
            failed = []
            updated = 0
            orphaned = 0

            if repair:
                for ch in chunks:
                    meta = getattr(ch.embedding, "status", None)
                    has_emb = getattr(ch.embedding, "embedding_id", None)

                    if has_emb and meta == "completed" and ch.embedding_status != "embedded":
                        ch.embedding_status = "embedded"
                        ch.save(update_fields=["embedding_status"])
                        updated += 1
                    elif not has_emb and ch.embedding_status == "embedded":
                        ch.embedding_status = "pending"
                        ch.save(update_fields=["embedding_status"])
                        orphaned += 1

            embedded = chunks.filter(embedding_status="embedded").count()
            failed = list(
                chunks.filter(embedding_status="failed").values_list("order", flat=True)
            )

            progress, created = DocumentProgress.objects.get_or_create(
                document=document,
                defaults={
                    "title": document.title,
                    "total_chunks": total,
                    "processed": total,
                    "embedded_chunks": embedded,
                    "failed_chunks": failed,
                    "status": "completed" if embedded == total else "failed",
                }
            )

            if not created and repair:
                progress.total_chunks = total
                progress.processed = total
                progress.embedded_chunks = embedded
                progress.failed_chunks = failed
                progress.status = "completed" if embedded == total else "failed"
                progress.save()
                self.stdout.write(f"🔧 Repaired: {document.title} -> {embedded}/{total} embedded")
            else:
                self.stdout.write(f"✅ Verified: {document.title} -> {embedded}/{total} embedded")

            if updated > 0 or orphaned > 0:
                self.stdout.write(f"   ↪️ Fixed statuses: {updated} updated, {orphaned} orphaned")