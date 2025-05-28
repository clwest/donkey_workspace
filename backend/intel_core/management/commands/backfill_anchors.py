from django.core.management.base import BaseCommand
from intel_core.models import DocumentChunk
from memory.models import SymbolicMemoryAnchor


class Command(BaseCommand):
    """Attach a SymbolicMemoryAnchor to matching document chunks."""

    help = "Backfill glossary anchors onto document chunks based on slug match"

    def add_arguments(self, parser):
        parser.add_argument("--slug", type=str)
        parser.add_argument("--only-focus", action="store_true")

    def handle(self, *args, **options):
        slug = options.get("slug")
        qs = SymbolicMemoryAnchor.objects.all()
        if options.get("only_focus"):
            qs = qs.filter(is_focus_term=True)
        if slug:
            qs = qs.filter(slug=slug)
        anchors = list(qs)
        if slug and not anchors:
            self.stdout.write(self.style.ERROR(f"Anchor '{slug}' not found."))
            return

        total = 0
        for anchor in anchors:
            matches = DocumentChunk.objects.filter(
                text__icontains=anchor.slug.replace("-", " ")
            )
            for chunk in matches:
                if not chunk.anchor:
                    chunk.anchor = anchor
                    chunk.save()
                    total += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Backfilled {total} chunks for anchor '{slug or 'all'}'."
            )
        )
