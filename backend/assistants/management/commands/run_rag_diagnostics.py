import json
from django.core.management.base import BaseCommand
from assistants.models import Assistant
from assistants.utils.resolve import resolve_assistant
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
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit number of anchors per assistant",
        )

    def handle(self, *args, **options):
        assistant_slug = options.get("assistant")
        disable_scope = options.get("disable_scope", False)
        out_path = options.get("output")
        limit = options.get("limit")

        if assistant_slug:
            assistant = resolve_assistant(assistant_slug)
            if not assistant:
                self.stdout.write(
                    self.style.ERROR(f"No assistant found with identifier '{assistant_slug}'")
                )
                return

            result = run_assistant_rag_test(
                assistant,
                limit=limit,
                disable_scope=disable_scope,
            )
            results = [result]
        else:
            results = []
            for assistant in Assistant.objects.all():
                result = run_assistant_rag_test(
                    assistant,
                    limit=limit,
                    disable_scope=disable_scope,
                )
                results.append(result)

        if out_path:
            with open(out_path, "w") as f:
                json.dump(results, f, indent=2)

        for r in results:
            rate = f"{r['pass_rate']*100:.1f}%"
            self.stdout.write(
                f"{r['assistant']}: {r['issues_found']} issues across {r['tested']} anchors ({rate})"
            )
