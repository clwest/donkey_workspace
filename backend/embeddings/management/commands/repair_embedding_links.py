from django.core.management.base import BaseCommand
from embeddings.utils import fix_embedding_links


class Command(BaseCommand):
    """Repair Embedding content links."""

    help = "Repair Embedding.content_type, object_id and content_id fields"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=None)
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--include-memory", action="store_true")  # ✅ add this line

    def handle(self, *args, **options):
        limit = options.get("limit")
        dry_run = options.get("dry_run")
        include_memory = options.get("include_memory")  # ✅ read flag

        result = fix_embedding_links(
            limit=limit,
            dry_run=dry_run,
            include_memory=include_memory  # ✅ pass into helper
        )