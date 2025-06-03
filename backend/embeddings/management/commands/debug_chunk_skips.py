from django.core.management.base import BaseCommand
from intel_core.models import DocumentChunk as Chunk


class Command(BaseCommand):
    help = "Show debug info on skipped chunks for a document"

    def add_arguments(self, parser):
        parser.add_argument("--doc-id", type=str, required=True)

    def handle(self, *args, **options):
        from embeddings.utils.chunk_retriever import should_embed_chunk

        chunks = Chunk.objects.filter(document_id=options["doc_id"]).order_by("order")
        for chunk in chunks:
            if should_embed_chunk(chunk):
                if getattr(chunk, "force_embed", False):
                    print(f"⚡️ Force Embed: Chunk {chunk.order} | Score={chunk.score}")
                else:
                    print(f"✅ Embeddable: Chunk {chunk.order} | Score={chunk.score}")
            else:
                print(f"❌ Skipped: Chunk {chunk.order} | Score={chunk.score}")
