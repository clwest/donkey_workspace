from django.core.management.base import BaseCommand
from memory.utils import queue_drifted_reflections

class Command(BaseCommand):
    help = "Queue drifted reflections for replay"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", dest="assistant", default=None)

    def handle(self, *args, **options):
        assistant_slug = options.get("assistant")
        count = queue_drifted_reflections(assistant_slug=assistant_slug)
        self.stdout.write(self.style.SUCCESS(f"Queued {count} reflections"))
