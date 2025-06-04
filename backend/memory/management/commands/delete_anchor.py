from django.core.management.base import BaseCommand
from memory.models import SymbolicMemoryAnchor
from intel_core.models import DocumentChunk


class Command(BaseCommand):
    """Delete a SymbolicMemoryAnchor and clean up chunk references."""

    help = "Delete glossary anchor and remove matches from chunks"

    def add_arguments(self, parser):
        parser.add_argument("--slug", required=True)

    def handle(self, *args, **options):
        slug = options["slug"]
        try:
            anchor = SymbolicMemoryAnchor.objects.get(slug=slug)
        except SymbolicMemoryAnchor.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Anchor '{slug}' not found."))
            return

        DocumentChunk.objects.filter(anchor=anchor).update(anchor=None)
        for chunk in DocumentChunk.objects.filter(matched_anchors__contains=[slug]):
            anchors = [a for a in chunk.matched_anchors if a != slug]
            chunk.matched_anchors = anchors
            chunk.save(update_fields=["matched_anchors"])

        anchor.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted anchor '{slug}'."))
