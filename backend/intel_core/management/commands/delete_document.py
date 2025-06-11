from django.core.management.base import BaseCommand
from intel_core.models import Document, DocumentChunk, EmbeddingMetadata
from memory.models import MemoryEntry
import sys

class Command(BaseCommand):
    help = "Deletes a document and its related chunks/memories by slug or ID"

    def add_arguments(self, parser):
        parser.add_argument('--slug', type=str, help='Document slug')
        parser.add_argument('--doc-id', type=str, help='Document UUID')
        parser.add_argument('--soft', action='store_true', help='Soft delete')
        parser.add_argument('--purge', action='store_true', help='Permanently remove soft-deleted records')

    def handle(self, *args, **options):
        doc_qs = Document.all_objects
        doc = None
        if options['slug']:
            doc = doc_qs.filter(slug=options['slug']).first()
        elif options['doc_id']:
            doc = doc_qs.filter(id=options['doc_id']).first()
        

        if not doc:
            self.stderr.write("❌ Document not found.")
            sys.exit(1)

        if options['purge']:
            if not doc.is_deleted:
                self.stderr.write('❌ Document is not soft-deleted.')
                sys.exit(1)
            self.stdout.write(f"🗑️ Purging document: {doc.title} ({doc.slug})")
            DocumentChunk.all_objects.filter(document=doc).delete()
            EmbeddingMetadata.all_objects.filter(chunk__document=doc).delete()
            MemoryEntry.objects.filter(document=doc).delete()
            doc.delete()
            self.stdout.write('✅ Purged document and related records.')
            return

        if options['soft']:
            self.stdout.write(f"🗑️ Soft deleting document: {doc.title} ({doc.slug})")
            doc.is_deleted = True
            doc.save(update_fields=['is_deleted'])
            DocumentChunk.all_objects.filter(document=doc).update(is_deleted=True)
            EmbeddingMetadata.all_objects.filter(chunk__document=doc).update(is_deleted=True)
            MemoryEntry.objects.filter(document=doc).delete()
            self.stdout.write('✅ Marked as deleted.')
            return

        self.stdout.write(f"🗑️ Deleting document: {doc.title} ({doc.slug})")
        chunks_deleted, _ = DocumentChunk.all_objects.filter(document=doc).delete()
        EmbeddingMetadata.all_objects.filter(chunk__document=doc).delete()
        memories_deleted, _ = MemoryEntry.objects.filter(document=doc).delete()
        doc.delete()
        self.stdout.write(
            f"✅ Deleted {chunks_deleted} chunks and {memories_deleted} memory entries."
        )

