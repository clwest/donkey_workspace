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

        for doc in docs:
            chunks = DocumentChunk.objects.filter(document=doc)
            total = chunks.count()
            embedded = chunks.filter(embedding_status='embedded').count()
            failed = chunks.filter(embedding_status='failed').count()

            progress, created = DocumentProgress.objects.get_or_create(
                document=doc,
                defaults={
                    'title': doc.title,
                    'total_chunks': total,
                    'processed': total,
                    'embedded_chunks': embedded,
                    'failed_chunks': [],
                    'status': 'completed' if embedded == total else 'failed',
                }
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