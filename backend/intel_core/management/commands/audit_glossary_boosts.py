from django.core.management.base import BaseCommand
from assistants.utils.resolve import resolve_assistant
from memory.models import SymbolicMemoryAnchor
from intel_core.models import DocumentChunk


class Command(BaseCommand):
    """Audit anchors with fallback scores but no glossary chunk matches."""

    help = "List anchors with fallback scores but zero glossary chunk matches"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True)

    def handle(self, *args, **options):
        slug = options["assistant"]
        assistant = resolve_assistant(slug)
        if not assistant:
            self.stderr.write(self.style.ERROR(f"Assistant '{slug}' not found."))
            return

        anchors = SymbolicMemoryAnchor.objects.filter(assistant=assistant)
        if not anchors.exists():
            self.stdout.write("No anchors found for this assistant.")
            return

        found = False
        for anchor in anchors:
            score = anchor.fallback_score or 0.0
            if score <= 0:
                continue
            match_count = DocumentChunk.objects.filter(anchor=anchor).count()
            if match_count == 0:
                self.stdout.write(
                    f"{assistant.slug}\t{anchor.slug}\t{score:.2f}\t{match_count}"
                )
                found = True
        if not found:
            self.stdout.write("No fallback boosts without matches found.")
