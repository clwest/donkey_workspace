from django.core.management.base import BaseCommand
from django.db.models import Sum
from assistants.utils.resolve import resolve_assistant
from memory.models import SymbolicMemoryAnchor


class Command(BaseCommand):
    """Recalculate mutation_score for anchors based on reinforcement logs"""

    help = "Recalculate anchor mutation scores"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=False)
        parser.add_argument("--debug", action="store_true")

    def handle(self, *args, **options):
        slug = options.get("assistant")
        debug = options.get("debug")
        anchors = SymbolicMemoryAnchor.objects.all()
        if slug:
            assistant = resolve_assistant(slug)
            if not assistant:
                self.stderr.write(self.style.ERROR(f"Assistant '{slug}' not found"))
                return
            anchors = anchors.filter(assistant=assistant)
        for anchor in anchors:
            total = (
                anchor.reinforcement_log.aggregate(total=Sum("score_delta")).get(
                    "total"
                )
                or 0.0
            )
            anchor.mutation_score = total
            anchor.save(update_fields=["mutation_score"])
            if debug:
                self.stdout.write(f"{anchor.slug}: {total:.2f}")
        if debug:
            summary = (
                anchors.values("assistant__slug")
                .annotate(total=Sum("mutation_score"))
                .order_by("-total")
            )
            for row in summary:
                self.stdout.write(f"{row['assistant__slug']}: {row['total']:.2f}")
