from django.core.management.base import BaseCommand
from assistants.models import Assistant
from memory.glossary_keeper import run_keeper_tasks


class Command(BaseCommand):
    """Run the Glossary Keeper daemon for maintenance."""

    help = "Analyze glossary anchors for drift and propose mutations"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Assistant slug to scan", required=False)
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--limit", type=int)
        parser.add_argument("--min-drift", type=float, default=0.5)

    def handle(self, *args, **options):
        slug = options.get("assistant")
        assistant = None
        if slug:
            try:
                assistant = Assistant.objects.get(slug=slug)
            except Assistant.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Assistant '{slug}' not found"))
                return
        count = run_keeper_tasks(
            assistant=assistant,
            dry_run=options.get("dry_run", False),
            limit=options.get("limit"),
            min_drift=options.get("min_drift", 0.5),
        )
        self.stdout.write(self.style.SUCCESS(f"Processed {count} anchors"))

