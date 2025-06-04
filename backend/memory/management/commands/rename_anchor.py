from django.core.management.base import BaseCommand
from memory.models import SymbolicMemoryAnchor
from intel_core.models import DocumentChunk


class Command(BaseCommand):
    """Rename a SymbolicMemoryAnchor slug and update chunk references."""

    help = "Rename glossary anchor"

    def add_arguments(self, parser):
        parser.add_argument("--from", dest="old", required=True)
        parser.add_argument("--to", dest="new", required=True)

    def handle(self, *args, **options):
        old = options["old"]
        new = options["new"]
        try:
            anchor = SymbolicMemoryAnchor.objects.get(slug=old)
        except SymbolicMemoryAnchor.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Anchor '{old}' not found."))
            return
        if SymbolicMemoryAnchor.objects.filter(slug=new).exclude(id=anchor.id).exists():
            self.stderr.write(self.style.ERROR(f"Slug '{new}' already in use."))
            return

        prev_slug = anchor.slug
        anchor.slug = new
        anchor.label = new.replace("-", " ").title()
        anchor.save()

        chunks = DocumentChunk.objects.filter(matched_anchors__contains=[prev_slug])
        for chunk in chunks:
            anchors = [a for a in chunk.matched_anchors if a != prev_slug]
            if new not in anchors:
                anchors.append(new)
            chunk.matched_anchors = anchors
            if chunk.anchor_id == anchor.id:
                chunk.anchor = anchor
            chunk.save(update_fields=["matched_anchors", "anchor"])

        self.stdout.write(self.style.SUCCESS(f"Renamed '{old}' -> '{new}'"))
