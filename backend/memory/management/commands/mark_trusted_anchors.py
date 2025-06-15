from django.core.management.base import BaseCommand
from django.utils import timezone
from assistants.utils.resolve import resolve_assistant
from memory.models import SymbolicMemoryAnchor
from assistants.utils.thought_logger import log_symbolic_thought


class Command(BaseCommand):
    help = "Mark anchors with mutation_score >= threshold as trusted"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True, help="Assistant slug")
        parser.add_argument("--threshold", type=float, default=0.0)

    def handle(self, *args, **options):
        assistant = resolve_assistant(options["assistant"])
        if not assistant:
            self.stderr.write(self.style.ERROR("Assistant not found"))
            return
        threshold = options["threshold"]
        anchors = SymbolicMemoryAnchor.objects.filter(
            assistant=assistant, mutation_score__gte=threshold
        )
        updated = anchors.update(
            is_trusted=True, last_verified_at=timezone.now()
        )
        self.stdout.write(
            self.style.SUCCESS(f"Marked {updated} anchors as trusted")
        )

        log_symbolic_thought(
            assistant,
            category="trust",
            thought=f"Trusted {updated} anchors",
            thought_type="update",
            tool_name="trust_calc",
            tool_result_summary=f"{updated} anchors",
            origin="trust_calc",
        )
