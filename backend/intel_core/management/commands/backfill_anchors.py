from django.core.management.base import BaseCommand
from intel_core.models import DocumentChunk
from memory.models import SymbolicMemoryAnchor

class Command(BaseCommand):
    help = "Backfill glossary anchors onto document chunks based on slug match"

    def add_arguments(self, parser):
        parser.add_argument("--slug", type=str, required=True)

    def handle(self, *args, **options):
        slug = options["slug"]
        try:
            anchor = SymbolicMemoryAnchor.objects.get(slug=slug)
        except SymbolicMemoryAnchor.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Anchor '{slug}' not found."))
            return

        matches = DocumentChunk.objects.filter(text__icontains=slug.replace("-", " "))
        updated = 0
        for chunk in matches:
            if not chunk.anchor:
                chunk.anchor = anchor
                chunk.save()
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(f"Backfilled {updated} chunks for anchor '{slug}'.")
        )