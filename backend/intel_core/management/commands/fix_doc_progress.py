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

        for doc in docs:
            chunks = DocumentChunk.objects.filter(document=doc)
            total = chunks.count()
            embedded = chunks.filter(embedding_status="embedded").count()
            failed = list(chunks.filter(embedding_status="failed").values_list("order", flat=True))

            fixed = 0
            orphaned = 0

            if options['repair']:
                for ch in chunks:
                    meta = ch.embedding
                    has_emb = getattr(meta, "embedding_id", None)
                    meta_status = getattr(meta, "status", None)

                    if has_emb and meta_status == "completed" and ch.embedding_status != "embedded":
                        ch.embedding_status = "embedded"
                        ch.save(update_fields=["embedding_status"])
                        fixed += 1
                    elif not has_emb and ch.embedding_status == "embedded":
                        ch.embedding_status = "pending"
                        ch.save(update_fields=["embedding_status"])
                        orphaned += 1

                embedded = chunks.filter(embedding_status="embedded").count()

            progress, created = DocumentProgress.objects.get_or_create(
                document=doc,
                defaults={
                    "title": doc.title,
                    "total_chunks": total,
                    "processed": total,
                    "embedded_chunks": embedded,
                    "failed_chunks": failed,
                    "status": "completed" if embedded == total else "failed",
                }
            )

            if not created:
                if options['repair']:
                    progress.total_chunks = total
                    progress.processed = total
                    progress.embedded_chunks = embedded
                    progress.failed_chunks = failed
                    progress.status = "completed" if embedded == total else "failed"
                    progress.save()
                    self.stdout.write(f"🔧 Repaired: {doc.title} -> {embedded}/{total} embedded")
                else:
                    self.stdout.write(f"✅ Verified: {doc.title} -> {embedded}/{total} embedded")
            else:
                self.stdout.write(f"➕ Created progress: {doc.title} -> {embedded}/{total} embedded")

            if options['repair']:
                self.stdout.write(f"   ↪️ Fixed statuses: {fixed} updated, {orphaned} orphaned")