from django.core.management.base import BaseCommand
from mcp_core.models import DevDoc
from intel_core.utils.processing import _create_document_chunks
from intel_core.models import Document, DocumentChunk
from embeddings.tasks import embed_and_store

class Command(BaseCommand):
    help = "Create missing chunks for DevDocs and ensure embeddings"

    def handle(self, *args, **options):
        created = 0
        skipped = 0
        for devdoc in DevDoc.objects.all():
            document = devdoc.linked_document
            if not document:
                document = Document.objects.filter(slug=devdoc.slug).first()
                if not document:
                    self.stdout.write(self.style.WARNING(f"No document for {devdoc.slug}"))
                    skipped += 1
                    continue
                devdoc.linked_document = document
                devdoc.save(update_fields=["linked_document"])
            if not DocumentChunk.objects.filter(document=document).exists():
                _create_document_chunks(document)
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Chunks created for {document.slug}"))
            else:
                skipped += 1
            for ch in document.chunks.filter(embedding__isnull=True):
                ch.embedding_status = "pending"
                ch.save(update_fields=["embedding_status"])
                embed_and_store.delay(str(ch.id))
        self.stdout.write(self.style.SUCCESS(f"Completed. Created {created}, skipped {skipped}"))
