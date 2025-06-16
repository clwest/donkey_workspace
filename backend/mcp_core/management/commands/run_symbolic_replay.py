from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404
from assistants.models import Assistant
from assistants.models.thoughts import AssistantThoughtLog
from memory.models import ReplayThreadLog, DriftAnalysisSnapshot
from utils.similarity import score_drift
from difflib import unified_diff


class Command(BaseCommand):
    help = "Run symbolic replay for an assistant's recent thoughts"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True)
        parser.add_argument("--limit", type=int, default=5)

    def handle(self, *args, **options):
        slug = options["assistant"]
        limit = options["limit"]
        assistant = get_object_or_404(Assistant, slug=slug)
        thoughts = (
            AssistantThoughtLog.objects.filter(assistant=assistant)
            .order_by("-created_at")[:limit]
        )
        replay_log = ReplayThreadLog.objects.create(assistant=assistant)
        total = 0
        score_total = 0.0
        for t in thoughts:
            regenerated = t.thought  # Stub regeneration
            drift = score_drift(t.thought, regenerated)
            diff_text = "\n".join(
                unified_diff(
                    t.thought.splitlines(),
                    regenerated.splitlines(),
                    lineterm="",
                )
            )
            DriftAnalysisSnapshot.objects.create(
                replay_log=replay_log,
                thought_log=t,
                original_text=t.thought,
                replayed_text=regenerated,
                diff_text=diff_text,
                drift_score=drift,
            )
            score_total += drift
            total += 1
        replay_log.summary_count = total
        replay_log.drift_score = score_total / total if total else 0.0
        replay_log.save(update_fields=["summary_count", "drift_score"])
        self.stdout.write(self.style.SUCCESS(f"Replayed {total} thoughts"))
