from django.core.management.base import BaseCommand
from memory.models import RAGGroundingLog

class Command(BaseCommand):
    """Inspect RAGGroundingLog fallback reasons and counts."""

    help = "Show counts of fallback reasons from recent RAG logs"

    def handle(self, *args, **options):
        reasons = {}
        for log in RAGGroundingLog.objects.exclude(fallback_reason__isnull=True):
            reason = log.fallback_reason or "unknown"
            reasons[reason] = reasons.get(reason, 0) + 1
        if not reasons:
            self.stdout.write("No fallback reasons recorded.")
            return
        self.stdout.write("Fallback Reason Counts:")
        for r, cnt in reasons.items():
            self.stdout.write(f"- {r}: {cnt}")
