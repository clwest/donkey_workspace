from django.core.management.base import BaseCommand
from intel_core.models import DocumentChunk
from memory.models import SymbolicMemoryAnchor
from utils.inspection_helpers import bool_icon, print_glossary_debug_table


class Command(BaseCommand):
    """Inspect glossary chunks associated with a given anchor slug."""

    help = "Inspect glossary chunk linkage for a given anchor slug"

    def add_arguments(self, parser):
        parser.add_argument("--slug", type=str, required=True)
        parser.add_argument(
            "--include-incomplete",
            action="store_true",
            help="Include chunks missing embeddings or scores",
        )

    def handle(self, *args, **options):
        slug = options["slug"]
        include_incomplete = options.get("include_incomplete", False)

        try:
            anchor = SymbolicMemoryAnchor.objects.get(slug=slug)
        except SymbolicMemoryAnchor.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Anchor '{slug}' not found."))
            return

        chunks = (
            DocumentChunk.objects.filter(anchor=anchor)
            .select_related("document")
            .order_by("order")
        )
        if not include_incomplete:
            chunks = chunks.exclude(embedding__isnull=True).exclude(score__isnull=True)

        print_glossary_debug_table(self.stdout, slug, chunks)
