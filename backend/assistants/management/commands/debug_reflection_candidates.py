from django.core.management.base import BaseCommand
from assistants.utils.resolve import resolve_assistant
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine

class Command(BaseCommand):
    help = "Preview reflection candidate memories for an assistant"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True)
        parser.add_argument("--limit", type=int, default=30)

    def handle(self, *args, **options):
        identifier = options["assistant"]
        limit = options["limit"]
        assistant = resolve_assistant(identifier)
        if not assistant:
            self.stderr.write(self.style.ERROR(f"Assistant '{identifier}' not found"))
            return
        engine = AssistantReflectionEngine(assistant)
        engine.get_memory_entries(limit=limit, verbose=True)
