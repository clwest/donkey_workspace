from django.core.management.base import BaseCommand

from assistants.models import Assistant
from intel_core.utils.infer_anchors_from_memory import infer_symbolic_anchors_from_memory

class Command(BaseCommand):
    """Persist anchors inferred from assistant memory."""

    help = "Persist AI-inferred glossary anchors from memory"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", type=str)
        parser.add_argument("--all", action="store_true")

    def handle(self, *args, **options):
        slug = options.get("assistant")
        process_all = options.get("all")
        if not slug and not process_all:
            self.stdout.write(self.style.ERROR("Specify --assistant=<slug> or --all"))
            return

        assistants = Assistant.objects.all()
        if not process_all:
            assistants = assistants.filter(slug=slug)
            if not assistants.exists():
                self.stdout.write(self.style.ERROR(f"Assistant '{slug}' not found."))
                return

        for assistant in assistants:
            self.stdout.write(f"🔍 Persisting anchors for {assistant.slug}...")
            _, created = infer_symbolic_anchors_from_memory(assistant)
            self.stdout.write(
                self.style.SUCCESS(f"Saved {created} inferred anchors for {assistant.slug}")
            )

