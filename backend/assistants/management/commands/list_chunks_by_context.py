from django.core.management.base import BaseCommand
from intel_core.models import DocumentChunk
from assistants.models import Assistant

class Command(BaseCommand):
    help = "List all document chunks linked to an assistant's memory context"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", type=str, required=True, help="Assistant slug")

    def handle(self, *args, **kwargs):
        slug = kwargs["assistant"]
        try:
            assistant = Assistant.objects.get(slug=slug)
        except Assistant.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"No assistant found with slug '{slug}'"))
            return

        memory_context_id = assistant.memory_context.id
        chunks = DocumentChunk.objects.filter(document__memory_context=assistant.memory_context)

        if not chunks.exists():
            self.stdout.write(f"No chunks linked to assistant '{slug}' (context {memory_context_id})")
            return

        self.stdout.write(f"\nChunks for Assistant '{slug}' [Context ID: {memory_context_id}]\n")
        self.stdout.write("-" * 120)
        self.stdout.write(
            f"{'Chunk ID':<36} {'Doc ID':<36} {'Title':<30} {'Status':<10}"
        )
        self.stdout.write("-" * 120)

        for chunk in DocumentChunk.objects.filter(document__memory_context=assistant.memory_context).select_related("document"):
            status = chunk.embedding_status
            title = chunk.document.title if chunk.document else "No Title"
            chunk_id = str(chunk.id)
            document_id = str(chunk.document_id)
            self.stdout.write(
                f"{chunk_id:<36} {document_id:<36} {title[:30]:<30} {status:<10}"
            )
