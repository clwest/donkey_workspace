from collections import Counter
import re

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db.models import Count, Avg
from django.utils.text import slugify

from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor, RAGGroundingLog, MemoryEntry
from mcp_core.models import Tag
from embeddings.helpers.helper_tagging import generate_tags_for_memory

TOKEN_RE = re.compile(r"[a-zA-Z0-9-]{3,}")

class Command(BaseCommand):
    help = "Phase Ω.10.r - RAG Recall Correction + Memory Expansion"

    def handle(self, *args, **options):
        weak_assistants = (
            Assistant.objects.annotate(anchor_total=Count("anchor_suggestions"))
            .filter(anchor_total__gt=100)
        )
        for assistant in weak_assistants:
            logs = RAGGroundingLog.objects.filter(assistant=assistant)
            if not logs.exists():
                continue
            hits = logs.filter(fallback_triggered=False).count()
            match_rate = hits / logs.count() if logs.count() else 0.0
            if match_rate >= 0.1:
                continue
            self.stdout.write(self.style.WARNING(
                f"Weak anchor match for {assistant.slug}: {match_rate:.2f}"
            ))
            self._repair_anchors(assistant, logs)
            self._expand_from_memory(assistant)
            call_command("validate_anchors", stdout=self.stdout)
            try:
                call_command("run_rag_tests", "--assistant", assistant.slug, stdout=self.stdout)
            except Exception:
                self.stdout.write(self.style.ERROR("run_rag_tests failed"))

    def _repair_anchors(self, assistant, logs):
        for anchor in SymbolicMemoryAnchor.objects.filter(assistant=assistant):
            anchor_logs = logs.filter(expected_anchor=anchor.slug)
            avg_score = anchor_logs.aggregate(avg=Avg("adjusted_score")).get("avg") or 0.0
            if anchor.auto_suppressed:
                anchor.is_unstable = True
                tags = generate_tags_for_memory(anchor.label)
                for t in tags:
                    tag_slug = slugify(t)
                    tag, _ = Tag.objects.get_or_create(slug=tag_slug, defaults={"name": t})
                    anchor.tags.add(tag)
                anchor.save(update_fields=["is_unstable"])
                self.stdout.write(f"  Suppressed {anchor.slug}")
            elif avg_score < 0.1 and anchor_logs.exists():
                tags = generate_tags_for_memory(anchor.label)
                for t in tags:
                    tag_slug = slugify(t)
                    tag, _ = Tag.objects.get_or_create(slug=tag_slug, defaults={"name": t})
                    anchor.tags.add(tag)

    def _expand_from_memory(self, assistant):
        counter = Counter()
        for m in MemoryEntry.objects.filter(assistant=assistant, is_active=True)[:1000]:
            counter.update(TOKEN_RE.findall(m.event.lower()))
        for token, _ in counter.most_common(20):
            slug = slugify(token)
            if SymbolicMemoryAnchor.objects.filter(slug=slug).exists():
                continue
            SymbolicMemoryAnchor.objects.create(
                slug=slug,
                label=token.title(),
                source="memory_token",
                assistant=assistant,
                memory_context=assistant.memory_context,
            )
            self.stdout.write(f"  Added anchor {token}")
