from django.core.management.base import BaseCommand
from django.db.models import Q

from assistants.models import Assistant
from intel_core.models import DocumentChunk
from memory.models import SymbolicMemoryAnchor


class Command(BaseCommand):
    """Re-scan chunks for glossary anchor matches."""

    help = "Recalculate glossary tags by matching anchor slugs in chunks"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True, type=str)
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--reset", action="store_true")

    def handle(self, *args, **options):
        assistant_slug = options["assistant"]
        dry_run = options.get("dry_run", False)
        reset = options.get("reset", False)

        try:
            assistant = Assistant.objects.get(slug=assistant_slug)
        except Assistant.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(f"Assistant '{assistant_slug}' not found.")
            )
            return

        chunks_qs = DocumentChunk.objects.filter(document__linked_assistants=assistant)

        if reset:
            reset_count = chunks_qs.update(is_glossary=False)
            self.stdout.write(f"Reset is_glossary on {reset_count} chunks")

        anchors = SymbolicMemoryAnchor.objects.filter(reinforced_by=assistant)
        if not anchors.exists():
            self.stdout.write(
                self.style.WARNING(f"No anchors linked to {assistant_slug}")
            )
            return

        for anchor in anchors:
            slug_lower = anchor.slug.lower()
            label_lower = anchor.label.lower()
            fp_list = list(
                DocumentChunk.objects.filter(anchor=anchor).values_list(
                    "fingerprint", flat=True
                )
            )

            q = Q(text__icontains=slug_lower) | Q(text__icontains=label_lower)
            if fp_list:
                q |= Q(fingerprint__in=fp_list)

            matches = list(chunks_qs.filter(q).distinct())
            if not matches:
                self.stdout.write(self.style.WARNING(f"⚠️ {anchor.slug}: no matches"))
                continue

            if not dry_run:
                for chunk in matches:
                    changed = False
                    if anchor.slug not in chunk.matched_anchors:
                        chunk.matched_anchors.append(anchor.slug)
                        changed = True
                    if not chunk.is_glossary:
                        chunk.is_glossary = True
                        changed = True
                    if changed:
                        chunk.save(update_fields=["matched_anchors", "is_glossary"])
            self.stdout.write(
                self.style.SUCCESS(f"✔️ {anchor.slug}: {len(matches)} chunks")
            )
