import json
from django.core.management.base import BaseCommand

from assistants.utils.assistant_boot import run_batch_self_tests


class Command(BaseCommand):
    help = "Run boot self-tests for all assistants"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            dest="output",
            help="Optional path to write JSON results",
            default=None,
        )

    def handle(self, *args, **options):
        results = run_batch_self_tests()
        out_path = options.get("output")
        if out_path:
            with open(out_path, "w") as f:
                json.dump(results, f, indent=2)
        for r in results:
            symbol = "✅" if r["passed"] else "❌"
            self.stdout.write(f"{symbol} {r['assistant']}")
        self.stdout.write(self.style.SUCCESS(f"{len(results)} assistants tested"))
