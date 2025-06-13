from django.core.management.base import BaseCommand
from assistants.utils.resolve import resolve_assistant
from memory.models import SymbolicMemoryAnchor, RAGGroundingLog, AnchorConfidenceLog
from django.db.models import Avg, F

class Command(BaseCommand):
    """Evaluate glossary anchor strength metrics."""

    help = "Compute anchor confidence metrics from past RAG logs"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", type=str, help="Assistant slug")
        parser.add_argument("--anchor", type=str, help="Anchor slug")
        parser.add_argument("--context-id", dest="context_id", type=str, help="MemoryContext ID")

    def handle(self, *args, **options):
        assistant_slug = options.get("assistant")
        anchor_slug = options.get("anchor")
        context_id = options.get("context_id")

        assistant = None
        if assistant_slug:
            assistant = resolve_assistant(assistant_slug)
            if not assistant:
                self.stderr.write(self.style.ERROR(f"Assistant '{assistant_slug}' not found"))
                return

        anchors = SymbolicMemoryAnchor.objects.all()
        if anchor_slug:
            anchors = anchors.filter(slug=anchor_slug)
        if context_id:
            anchors = anchors.filter(memory_context_id=context_id)
        if assistant:
            anchors = anchors.filter(memory_context=assistant.memory_context)

        for anchor in anchors:
            qs = RAGGroundingLog.objects.filter(expected_anchor=anchor.slug)
            if assistant:
                qs = qs.filter(assistant=assistant)
            if context_id:
                qs = qs.filter(assistant__memory_context_id=context_id)
            total = qs.count()
            if not total:
                continue
            fallback_rate = qs.filter(fallback_triggered=True).count() / total
            avg_score = qs.aggregate(avg=Avg("adjusted_score"))['avg'] or 0.0
            hit_pct = qs.filter(glossary_hits__contains=[anchor.slug]).count() / total
            delta = qs.annotate(diff=F("corrected_score") - F("raw_score")).aggregate(avg=Avg("diff"))['avg'] or 0.0
            AnchorConfidenceLog.objects.create(
                anchor=anchor,
                assistant=assistant,
                memory_context_id=context_id,
                total_logs=total,
                fallback_rate=fallback_rate,
                avg_score=avg_score,
                glossary_hit_pct=hit_pct,
                score_delta_avg=delta,
            )
            self.stdout.write(
                f"{anchor.slug}: score={avg_score:.2f} fallback_rate={fallback_rate:.2f} hits={hit_pct:.2f}"
            )
