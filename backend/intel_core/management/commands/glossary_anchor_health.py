from django.core.management.base import BaseCommand
from django.db.models import Avg, Count, Q
from assistants.utils.resolve import resolve_assistant
from memory.models import SymbolicMemoryAnchor
from intel_core.models import DocumentChunk, GlossaryFallbackReflectionLog

class Command(BaseCommand):
    """Report glossary anchor match health for an assistant."""

    help = "Show glossary anchor match statistics"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True, type=str)

    def handle(self, *args, **options):
        slug = options["assistant"]
        assistant = resolve_assistant(slug)
        if not assistant:
            self.stdout.write(self.style.ERROR(f"Assistant '{slug}' not found."))
            return

        anchors = SymbolicMemoryAnchor.objects.filter(reinforced_by=assistant)
        total = anchors.count()
        if total == 0:
            self.stdout.write("No anchors linked to this assistant.")
            return

        anchor_stats = []
        total_chunks = 0
        total_score = 0.0

        for anchor in anchors:
            chunks = DocumentChunk.objects.filter(
                Q(anchor=anchor) | Q(matched_anchors__contains=[anchor.slug])
            )
            count = chunks.count()
            avg_score = chunks.aggregate(a=Avg("glossary_score"))["a"] or 0.0
            fallback_count = GlossaryFallbackReflectionLog.objects.filter(
                anchor_slug=anchor.slug
            ).count()
            anchor_stats.append((anchor.slug, count, avg_score, fallback_count))
            total_chunks += count
            total_score += avg_score * count

        avg_score_overall = total_score / total_chunks if total_chunks else 0.0

        self.stdout.write(f"Total anchors: {total}")
        self.stdout.write(f"Chunks matched: {total_chunks}")
        self.stdout.write(
            f"Average glossary_score: {avg_score_overall:.2f}"
        )

        weakest = sorted(anchor_stats, key=lambda x: x[2])[:10]
        if weakest:
            self.stdout.write("Top weak anchors:")
            for slug, count, score, fallback in weakest:
                self.stdout.write(
                    f"- {slug}: avg_score={score:.2f} chunks={count} fallback={fallback}"
                )
