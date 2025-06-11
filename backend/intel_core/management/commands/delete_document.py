from django.core.management.base import BaseCommand
from intel_core.models import Document
from memory.models import  MemoryEntry
from intel_core.models import DocumentChunk
import sys

class Command(BaseCommand):
    help = "Deletes a document and its related chunks/memories by slug or ID"

    def add_arguments(self, parser):
        parser.add_argument('--slug', type=str, help='Document slug')
        parser.add_argument('--id', type=str, help='Document UUID')

    def handle(self, *args, **options):
        doc = None
        if options['slug']:
            doc = Document.objects.filter(slug=options['slug']).first()
        elif options['id']:
            doc = Document.objects.filter(id=options['id']).first()

        if not doc:
            self.stderr.write("❌ Document not found.")
            sys.exit(1)

        self.stdout.write(f"🗑️ Deleting document: {doc.title} ({doc.slug})")

        # Delete related chunks and memory
        chunks_deleted, _ = DocumentChunk.objects.filter(document=doc).delete()
        memories_deleted, _ = MemoryEntry.objects.filter(document=doc).delete()
        doc.delete()

        self.stdout.write(f"✅ Deleted {chunks_deleted} chunks and {memories_deleted} memory entries.")