from django.core.management.base import BaseCommand
from embeddings.utils import fix_embedding_links


class Command(BaseCommand):
    """Repair Embedding content links."""

    help = "Repair Embedding.content_type, object_id and content_id fields"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=None)

    def handle(self, *args, **options):
        limit = options.get("limit")
        result = fix_embedding_links(limit=limit)
        self.stdout.write(f"Embeddings scanned: {result['scanned']}")
        self.stdout.write(f"Fixed: {result['fixed']}")
        self.stdout.write(f"Skipped: {result['skipped']}")
