from django.core.management.base import BaseCommand
from django.db.models import Avg, Count
from memory.models import RAGGroundingLog
from assistants.utils.resolve import resolve_assistant

class Command(BaseCommand):
    """Print average adjusted scores for fallback logs grouped by glossary term."""

    help = "Show fallback score ranges for glossary terms"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True, type=str)

    def handle(self, *args, **options):
        slug = options["assistant"]
        assistant = resolve_assistant(slug)
        if not assistant:
            self.stderr.write(self.style.ERROR(f"Assistant '{slug}' not found."))
            return

        qs = RAGGroundingLog.objects.filter(
            assistant=assistant, fallback_triggered=True
        ).exclude(expected_anchor="")
        if not qs.exists():
            self.stdout.write("No fallback logs found.")
            return

        stats = (
            qs.values("expected_anchor")
            .annotate(avg=Avg("adjusted_score"), count=Count("id"))
            .order_by("avg")
        )
        self.stdout.write("Fallback Score Averages:")
        for row in stats:
            anchor = row["expected_anchor"]
            avg_score = row["avg"] or 0.0
            count = row["count"]
            self.stdout.write(f"- {anchor}: avg_score={avg_score:.2f} ({count} logs)")
