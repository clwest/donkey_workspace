from django.core.management.base import BaseCommand
from assistants.utils.resolve import resolve_assistant
from assistants.utils.rag_diagnostics import run_assistant_rag_test

class Command(BaseCommand):
    """Simulate RAG queries for an assistant using glossary terms."""

    help = "Simulate glossary queries and log grounding results"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True, type=str)

    def handle(self, *args, **options):
        slug = options["assistant"]
        assistant = resolve_assistant(slug)
        if not assistant:
            self.stderr.write(self.style.ERROR(f"Assistant '{slug}' not found"))
            return
        result = run_assistant_rag_test(assistant)
        symbol = "✅" if result["passed"] else "❌"
        self.stdout.write(f"{symbol} {slug} ({len(result['issues'])} issues)")
