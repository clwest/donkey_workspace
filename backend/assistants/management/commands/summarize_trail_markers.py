from django.core.management.base import BaseCommand
from assistants.utils.resolve import resolve_assistant
from assistants.utils.trail_marker_summary import summarize_trail_markers


class Command(BaseCommand):
    help = "Generate a milestone summary from trail markers"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Assistant slug")

    def handle(self, *args, **options):
        identifier = options.get("assistant")
        if not identifier:
            self.stderr.write("Provide --assistant=slug or id")
            return
        assistant = resolve_assistant(identifier)
        if not assistant:
            self.stderr.write("Assistant not found")
            return
        entry = summarize_trail_markers(assistant)
        if not entry:
            self.stdout.write(self.style.WARNING("No trail markers"))
            return
        self.stdout.write(
            self.style.SUCCESS(
                f"{assistant.slug}: saved {entry.id} at {entry.created_at:%Y-%m-%d %H:%M}"
            )
        )
        preview = entry.summary.splitlines()[0][:120]
        self.stdout.write(preview)
