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
        chunks = DocumentChunk.objects.filter(memory_context_id=memory_context_id)

        if not chunks.exists():
            self.stdout.write(f"No chunks linked to assistant '{slug}' (context {memory_context_id})")
            return

        self.stdout.write(f"\nChunks for Assistant '{slug}' [Context ID: {memory_context_id}]\n")
        self.stdout.write("-" * 80)
        self.stdout.write(f"{'Chunk ID':<10} {'Doc ID':<10} {'Title':<30} {'Status':<10}")
        self.stdout.write("-" * 80)

        for chunk in chunks.select_related("document"):
            status = chunk.embedding_status
            title = chunk.document.title if chunk.document else "No Title"
            self.stdout.write(f"{chunk.id:<10} {chunk.document_id:<10} {title[:30]:<30} {status:<10}")