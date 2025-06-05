from django.core.management.base import BaseCommand
from intel_core.models import DocumentChunk


class Command(BaseCommand):
    """Audit DocumentChunks for embedding/glossary mismatches."""

    help = "List chunks with embeddings but mismatched status or missing glossary"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=50)

    def handle(self, *args, **options):
        limit = options["limit"]
        issues = []
        for chunk in DocumentChunk.objects.all()[:limit]:
            if chunk.embedding and chunk.embedding_status != "embedded":
                issues.append(f"{chunk.id} status={chunk.embedding_status} has embedding")
            if not chunk.embedding and chunk.embedding_status == "embedded":
                issues.append(f"{chunk.id} marked embedded but missing vector")
            if chunk.embedding and chunk.glossary_score == 0:
                issues.append(f"{chunk.id} embedded but glossary_score=0")
        if not issues:
            self.stdout.write("No integrity issues found")
            return
        self.stdout.write(f"Found {len(issues)} issues:")
        for line in issues:
            self.stdout.write("- " + line)
