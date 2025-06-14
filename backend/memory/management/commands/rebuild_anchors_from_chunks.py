from django.core.management.base import BaseCommand
from assistants.utils.resolve import resolve_assistant
from memory.utils import rebuild_anchors_from_chunks


class Command(BaseCommand):
    """Regenerate SymbolicMemoryAnchor terms from RAG playback chunks."""

    help = "Rebuild glossary anchors using high scoring RAG chunks"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Assistant slug or ID", required=False)
        parser.add_argument("--threshold", type=float, default=0.25)
        parser.add_argument("--top-n", dest="top_n", type=int, default=5)
        parser.add_argument("--doc-type", dest="doc_type")
        parser.add_argument("--replace", action="store_true")

    def handle(self, *args, **options):
        assistant = None
        slug = options.get("assistant")
        if slug:
            assistant = resolve_assistant(slug)
            if not assistant:
                self.stderr.write(self.style.ERROR("Assistant not found"))
                return

        created = rebuild_anchors_from_chunks(
            assistant,
            threshold=options["threshold"],
            top_n=options["top_n"],
            doc_type=options.get("doc_type"),
            replace=options.get("replace", False),
            stdout=self.stdout,
        )
        self.stdout.write(self.style.SUCCESS(f"Created {created} anchors"))
