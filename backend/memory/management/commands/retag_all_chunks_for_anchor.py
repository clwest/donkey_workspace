from django.core.management.base import BaseCommand
from memory.models import SymbolicMemoryAnchor
from intel_core.models import DocumentChunk
from intel_core.utils.glossary_tagging import _match_anchor


class Command(BaseCommand):
    """Recompute glossary matches for a single anchor across all chunks."""

    help = "Retag all document chunks for a glossary anchor"

    def add_arguments(self, parser):
        parser.add_argument("--slug", required=True)

    def handle(self, *args, **options):
        slug = options["slug"]
        try:
            anchor = SymbolicMemoryAnchor.objects.get(slug=slug)
        except SymbolicMemoryAnchor.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Anchor '{slug}' not found."))
            return

        updated = 0
        for chunk in DocumentChunk.objects.all().iterator():
            matched, _ = _match_anchor(anchor, chunk.text)
            anchors = list(chunk.matched_anchors)
            has = anchor.slug in anchors
            if matched and not has:
                anchors.append(anchor.slug)
                chunk.matched_anchors = anchors
                if not chunk.anchor_id:
                    chunk.anchor = anchor
                chunk.is_glossary = True
                chunk.save(update_fields=["matched_anchors", "anchor", "is_glossary"])
                updated += 1
            elif not matched and has:
                anchors.remove(anchor.slug)
                chunk.matched_anchors = anchors
                if chunk.anchor_id == anchor.id:
                    chunk.anchor = None
                chunk.save(update_fields=["matched_anchors", "anchor"])
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Retagged {updated} chunks for '{slug}'."))
