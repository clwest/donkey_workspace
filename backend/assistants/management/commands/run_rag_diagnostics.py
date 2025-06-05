import json
from django.core.management.base import BaseCommand
from assistants.models import Assistant
from assistants.utils.rag_diagnostics import run_assistant_rag_test

class Command(BaseCommand):
    """Run RAG self-tests for a specific assistant or all assistants."""

    help = "Execute RAG diagnostics with optional assistant scoping"

    def add_arguments(self, parser):
        parser.add_argument(
            "--assistant",
            type=str,
            help="Slug of the assistant to scope diagnostics to",
        )
        parser.add_argument(
            "--disable-scope",
            action="store_true",
            help="Run diagnostics across all chunks without scoping to memory_context",
        )
        parser.add_argument(
            "--output",
            dest="output",
            default=None,
            help="Optional path to write diagnostic output as JSON",
        )

    def handle(self, *args, **options):
        assistant_slug = options.get("assistant")
        disable_scope = options.get("disable_scope", False)
        out_path = options.get("output")

        if assistant_slug:
            try:
                assistant = Assistant.objects.get(slug=assistant_slug)
            except Assistant.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"No assistant found with slug '{assistant_slug}'"))
                return

            result = run_assistant_rag_test(assistant, disable_scope=disable_scope)
            results = [result]
        else:
            results = []
            for assistant in Assistant.objects.all():
                result = run_assistant_rag_test(assistant, disable_scope=disable_scope)
                results.append(result)

        if out_path:
            with open(out_path, "w") as f:
                json.dump(results, f, indent=2)

        for r in results:
            symbol = "✅" if r["passed"] else "❌"
            self.stdout.write(f"{symbol} {r['assistant']} ({len(r['issues'])} issues)")

        assistant_label = r.get("assistant", "unknown")
        issue_count = len(r.get("issues", []))
        self.stdout.write(f"{symbol} {assistant_label} ({issue_count} issues)")