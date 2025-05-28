from django.core.management.base import BaseCommand
from intel_core.models import DocumentChunk
from memory.models import SymbolicMemoryAnchor


class Command(BaseCommand):
    """Inspect glossary chunks associated with a given anchor slug."""

    help = "Inspect glossary chunk linkage for a given anchor slug"

    def add_arguments(self, parser):
        parser.add_argument("--slug", type=str, required=True)

    def handle(self, *args, **options):
        slug = options["slug"]
        try:
            anchor = SymbolicMemoryAnchor.objects.get(slug=slug)
        except SymbolicMemoryAnchor.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Anchor '{slug}' not found."))
            return

        all_chunks = DocumentChunk.objects.filter(text__icontains=slug.replace("-", " "))
        linked = all_chunks.filter(anchor=anchor)
        glossary = linked.filter(is_glossary=True)
        embedded = linked.exclude(embedding__isnull=True)

        self.stdout.write(self.style.MIGRATE_HEADING(f"📎 Anchor: {slug}"))
        self.stdout.write(f"Total Matches: {all_chunks.count()}")
        self.stdout.write(f"Linked to Anchor: {linked.count()}")
        self.stdout.write(f"Marked is_glossary: {glossary.count()}")
        self.stdout.write(f"Embedded: {embedded.count()}")
