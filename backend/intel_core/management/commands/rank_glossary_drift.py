from django.core.management.base import BaseCommand
from django.db.models import Avg, Count
from memory.models import RAGGroundingLog
from assistants.models import Assistant

class Command(BaseCommand):
    """Rank glossary terms by fallback frequency and score."""

    help = "Show glossary drift risk scores"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True, type=str)

    def handle(self, *args, **options):
        slug = options["assistant"]
        try:
            assistant = Assistant.objects.get(slug=slug)
        except Assistant.DoesNotExist:
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
            .order_by("-count")
        )
        self.stdout.write("| Term | Avg Score | Fallback Logs | Risk |")
        self.stdout.write("|------|-----------|--------------|------|")
        for row in stats:
            avg = row["avg"] or 0.0
            count = row["count"]
            if avg < 0.2 and count >= 3:
                risk = "HIGH"
            elif 0.2 <= avg <= 0.6:
                risk = "MEDIUM"
            else:
                risk = "HEALTHY"
            self.stdout.write(
                f"| {row['expected_anchor']} | {avg:.2f} | {count} | {risk} |"
            )
