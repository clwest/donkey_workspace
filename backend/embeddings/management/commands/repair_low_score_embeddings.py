from django.core.management.base import BaseCommand
from intel_core.models import DocumentChunk
from embeddings.tasks import embed_and_store

class Command(BaseCommand):
    help = "Re-embed or delete embeddings for chunks with low scores"

    def add_arguments(self, parser):
        parser.add_argument("--threshold", type=float, default=0.1)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        threshold = options["threshold"]
        dry_run = options["dry_run"]
        chunks = DocumentChunk.objects.filter(score__lte=threshold)
        count = 0
        for ch in chunks.select_related("embedding"):
            if ch.embedding:
                ch.embedding.is_deleted = True
                if not dry_run:
                    ch.embedding.save(update_fields=["is_deleted"])
                ch.embedding = None
            ch.embedding_status = "pending"
            ch.force_embed = True
            if not dry_run:
                ch.save(update_fields=["embedding", "embedding_status", "force_embed"])
                embed_and_store.delay(str(ch.id))
            count += 1
        self.stdout.write(f"Processed {count} chunks")
