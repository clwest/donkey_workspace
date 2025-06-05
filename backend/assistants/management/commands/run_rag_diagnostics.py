import json
from django.core.management.base import BaseCommand
from assistants.utils.rag_diagnostics import run_rag_diagnostics


class Command(BaseCommand):
    """Run RAG self-tests for all assistants."""

    help = "Execute RAG diagnostics across all assistants"

    def add_arguments(self, parser):
        parser.add_argument("--output", dest="output", default=None)

    def handle(self, *args, **options):
        results = run_rag_diagnostics()
        out_path = options.get("output")
        if out_path:
            with open(out_path, "w") as f:
                json.dump(results, f, indent=2)
        for r in results:
            symbol = "✅" if r["passed"] else "❌"
            self.stdout.write(f"{symbol} {r['assistant']} ({len(r['issues'])} issues)")
        self.stdout.write(self.style.SUCCESS(f"{len(results)} assistants tested"))
