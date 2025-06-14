from django.core.management.base import BaseCommand

from assistants.utils.resolve import resolve_assistant
from memory.utils import relink_anchor_chunks


class Command(BaseCommand):
    """Reconnect symbolic anchors to matching chunks."""

    help = "Reconnect anchors to chunks using embedding search or logs"

    def add_arguments(self, parser):
        parser.add_argument("--assistant")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--threshold", type=float, default=0.25)
        parser.add_argument("--purge-existing", action="store_true")

    def handle(self, *args, **options):
        assistant = None
        if options.get("assistant"):
            assistant = resolve_assistant(options["assistant"])
            if not assistant:
                self.stderr.write(self.style.ERROR("Assistant not found"))
                return

        count = relink_anchor_chunks(
            assistant=assistant,
            threshold=options["threshold"],
            purge=options["purge_existing"],
            dry_run=options["dry_run"],
            stdout=self.stdout,
        )
        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS(f"Would create {count} links"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Created {count} links"))
