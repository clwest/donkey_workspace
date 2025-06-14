from django.core.management.base import BaseCommand
from memory.models import SymbolicMemoryAnchor


class Command(BaseCommand):
    """List anchor mutations filtered by assistant or memory context."""

    help = "List mutated anchors"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Assistant slug")
        parser.add_argument("--context", help="Memory context id")

    def handle(self, *args, **options):
        qs = SymbolicMemoryAnchor.objects.exclude(mutated_reason__isnull=True)
        if options.get("assistant"):
            qs = qs.filter(assistant__slug=options["assistant"])
        if options.get("context"):
            qs = qs.filter(memory_context_id=options["context"])
        for a in qs.order_by("-created_at"):
            self.stdout.write(
                f"{a.slug} | from={a.mutated_from} | reason={a.mutated_reason}"
            )
