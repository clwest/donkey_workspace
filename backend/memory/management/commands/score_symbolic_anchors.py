from django.core.management.base import BaseCommand
from django.db.models import Avg, Count
from memory.models import SymbolicMemoryAnchor
from memory.models import RAGGroundingLog
from intel_core.models import GlossaryFallbackReflectionLog

class Command(BaseCommand):
    help = "Calculate anchor usage statistics"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Assistant slug", required=False)

    def handle(self, *args, **options):
        slug = options.get("assistant")
        anchors = SymbolicMemoryAnchor.objects.all()
        if slug:
            anchors = anchors.filter(assistant__slug=slug)
        for anchor in anchors:
            rag_qs = RAGGroundingLog.objects.filter(expected_anchor=anchor.slug)
            if anchor.assistant_id:
                rag_qs = rag_qs.filter(assistant_id=anchor.assistant_id)
            fb_qs = GlossaryFallbackReflectionLog.objects.filter(anchor_slug=anchor.slug)
            total_rag = rag_qs.count() + fb_qs.count()
            avg_score = rag_qs.aggregate(avg=Avg("adjusted_score")).get("avg") or 0.0
            fb_count = rag_qs.filter(fallback_triggered=True).count() + fb_qs.count()
            fallback_rate = fb_count / total_rag if total_rag else 0.0
            snapshot = {
                "rag_uses": rag_qs.count(),
                "fallback_logs": fb_qs.count(),
                "avg_score": round(avg_score, 4),
                "fallback_count": fb_count,
            }
            anchor.total_uses = total_rag
            anchor.avg_score = avg_score
            anchor.fallback_rate = fallback_rate
            anchor.score_snapshot = snapshot
            anchor.is_unstable = fallback_rate > 0.6 and avg_score < 0.15
            anchor.save(
                update_fields=[
                    "total_uses",
                    "avg_score",
                    "fallback_rate",
                    "score_snapshot",
                    "is_unstable",
                ]
            )
        self.stdout.write(self.style.SUCCESS(f"Scored {anchors.count()} anchors"))
