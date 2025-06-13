from django.core.management.base import BaseCommand
from memory.utils import queue_drifted_reflections

class Command(BaseCommand):
    help = "Queue drifted reflections for replay"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", dest="assistant", default=None)

    def handle(self, *args, **options):
        assistant_id = options.get("assistant")
        if assistant_id:
            from assistants.utils.resolve import resolve_assistant

            assistant = resolve_assistant(assistant_id)
            if not assistant:
                self.stderr.write(self.style.ERROR(f"Assistant '{assistant_id}' not found"))
                return
            assistant_slug = assistant.slug
        else:
            assistant_slug = None
        count = queue_drifted_reflections(assistant_slug=assistant_slug)
        self.stdout.write(self.style.SUCCESS(f"Queued {count} reflections"))
