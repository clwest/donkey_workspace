from django.core.management.base import BaseCommand
from django.db.models import Avg, Count
from assistants.models import Assistant
from intel_core.models import DocumentChunk, GlossaryFallbackReflectionLog
from memory.models import SymbolicMemoryAnchor, RAGGroundingLog
from mcp_core.models import Tag
from embeddings.helpers.helper_tagging import generate_tags_for_memory

class Command(BaseCommand):
    """Validate glossary anchors and report potential issues."""

    help = "Check SymbolicMemoryAnchor coverage and match quality"

    def add_arguments(self, parser):
        parser.add_argument(
            "--score-threshold",
            type=float,
            default=0.3,
            help="Avg score threshold for low-performing anchors",
        )
        parser.add_argument(
            "--match-rate",
            type=float,
            default=0.5,
            help="Minimum glossary hit rate per assistant",
        )

    def handle(self, *args, **options):
        score_th = options["score_threshold"]
        match_th = options["match_rate"]
        anchors = SymbolicMemoryAnchor.objects.all()
        for a in anchors:
            chunk_count = DocumentChunk.objects.filter(anchor=a).count()
            if chunk_count == 0:
                self.stdout.write(f"⚠️ {a.slug} has no linked chunks")
            logs = RAGGroundingLog.objects.filter(expected_anchor=a.slug)
            if not logs.exists():
                self.stdout.write(f"⚠️ {a.slug} never matched in queries")
            avg_score = logs.aggregate(avg=Avg("adjusted_score"))["avg"] or 0.0
            if avg_score < score_th:
                self.stdout.write(
                    f"❗ {a.slug} low avg score {avg_score:.2f}"
                )
                tags = generate_tags_for_memory(a.label)
                for t in tags:
                    tag, _ = Tag.objects.get_or_create(slug=t, defaults={"name": t})
                    a.tags.add(tag)
        dups = (
            SymbolicMemoryAnchor.objects.values("slug")
            .annotate(c=Count("id"))
            .filter(c__gt=1)
        )
        for d in dups:
            self.stdout.write(
                f"⚠️ Overlap: anchor '{d['slug']}' appears {d['c']} times"
            )
        for assistant in Assistant.objects.all():
            logs = RAGGroundingLog.objects.filter(assistant=assistant)
            if not logs.exists():
                continue
            hits = logs.filter(glossary_hits__len__gt=0).count()
            rate = hits / logs.count()
            if rate < match_th:
                self.stdout.write(
                    f"❗ Assistant {assistant.slug} match rate {rate:.2f}"
                )
        self.stdout.write(self.style.SUCCESS("Anchor validation complete"))
