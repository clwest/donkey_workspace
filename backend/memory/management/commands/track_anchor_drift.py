from datetime import timedelta
from django.core.management.base import BaseCommand
from django.db.models import Avg, Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from assistants.utils.resolve import resolve_assistant
from memory.models import SymbolicMemoryAnchor, RAGGroundingLog, AnchorDriftLog
from memory.glossary_keeper import (
    suggest_mutation_with_rationale,
    reflect_on_anchor_drift,
)


class Command(BaseCommand):
    """Track anchor drift over time and log metrics."""

    help = "Log anchor drift metrics and output score slopes"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True)
        parser.add_argument("--days", type=int, default=30)
        parser.add_argument("--log", action="store_true")

    def handle(self, *args, **options):
        assistant = resolve_assistant(options["assistant"])
        if not assistant:
            self.stderr.write(self.style.ERROR("Assistant not found"))
            return

        since = timezone.now() - timedelta(days=options["days"])
        anchors = SymbolicMemoryAnchor.objects.filter(
            memory_context=assistant.memory_context
        )
        for anchor in anchors:
            qs = RAGGroundingLog.objects.filter(
                assistant=assistant,
                expected_anchor=anchor.slug,
                created_at__gte=since,
            )
            if not qs.exists():
                continue
            daily = (
                qs.annotate(d=TruncDate("created_at"))
                .values("d")
                .annotate(
                    avg=Avg("adjusted_score"),
                    total=Count("id"),
                    fb=Count("id", filter=Q(fallback_triggered=True)),
                )
                .order_by("d")
            )
            scores = [row["avg"] or 0.0 for row in daily]
            slope = 0.0
            if len(scores) > 1:
                slope = (scores[-1] - scores[0]) / (len(scores) - 1)
            self.stdout.write(f"{anchor.slug}: slope={slope:.3f}")
            if options["log"] and daily:
                row = daily[-1]
                AnchorDriftLog.objects.update_or_create(
                    anchor=anchor,
                    observation_date=row["d"],
                    defaults={
                        "assistant": assistant,
                        "avg_score": row["avg"] or 0.0,
                        "fallback_rate": (
                            row["fb"] / row["total"] if row["total"] else 0.0
                        ),
                        "sample_size": row["total"],
                    },
                )
                if slope < -0.05 and row["avg"] < 0.4:
                    suggestion, rationale = suggest_mutation_with_rationale(anchor)
                    anchor.suggested_label = suggestion
                    anchor.mutation_status = "pending"
                    anchor.save(update_fields=["suggested_label", "mutation_status"])
                    reflect_on_anchor_drift(anchor, rationale, assistant=assistant)
                    self.stdout.write(
                        self.style.WARNING(
                            f"Drift detected for {anchor.slug}; mutation suggested"
                        )
                    )
