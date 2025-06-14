from django.core.management.base import BaseCommand
from intel_core.models import Document, DocumentChunk, DocumentUploadLog
from intel_core.utils import delete_failed_chunks
from intel_core.utils.processing import _create_document_chunks
from embeddings.tasks import embed_and_store
from assistants.models.assistant import Assistant

class Command(BaseCommand):
    help = "Repair failed or partial documents"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", type=str)
        parser.add_argument("--delete-chunks", action="store_true")
        parser.add_argument("--force-embed", action="store_true")
        parser.add_argument("--full-reset", action="store_true")

    def handle(self, *args, **options):
        qs = Document.objects.exclude(status="completed")
        if options.get("assistant"):
            slug = options["assistant"]
            assistant = Assistant.objects.filter(slug=slug).first() or Assistant.objects.filter(id=slug).first()
            if assistant:
                qs = qs.filter(linked_assistants=assistant)
        self.stdout.write(f"\U0001F50D Found {qs.count()} documents to repair")
        for doc in qs:
            self.stdout.write(f"\U0001F527 {doc.title} ({doc.id})")
            if options.get("full-reset") or options.get("delete-chunks"):
                removed = delete_failed_chunks(doc)
                self.stdout.write(f"   - Deleted {removed} failed chunks")
            if options.get("full-reset"):
                DocumentChunk.objects.filter(document=doc).delete()
                _create_document_chunks(doc)
            if options.get("force-embed") or options.get("full-reset"):
                for chunk in doc.chunks.filter(embedding__isnull=True):
                    chunk.embedding_status = "pending"
                    chunk.force_embed = True
                    chunk.save(update_fields=["embedding_status", "force_embed", "embedding"])
                    embed_and_store.delay(str(chunk.id))
            doc.status = "processing"
            doc.save(update_fields=["status"])
            DocumentUploadLog.objects.create(document=doc, action="retry")
        self.stdout.write(self.style.SUCCESS("Repair complete"))

