import logging
from django.core.management.base import BaseCommand
from django.utils import timezone

from assistants.models.reflection import AssistantReflectionLog
from memory.models import ReflectionReplayLog

logger = logging.getLogger(__name__)

PLACEHOLDERS = {
    "no meaningful reflection found",
    "n/a",
    "none",
    "",
}


class Command(BaseCommand):
    help = "Patch reflection summaries using replay data"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Assistant slug", default=None)
        parser.add_argument("--limit", type=int, default=100)

    def handle(self, *args, **options):
        slug = options.get("assistant")
        limit = options.get("limit")
        qs = AssistantReflectionLog.objects.all().order_by("-created_at")
        if slug:
            qs = qs.filter(assistant__slug=slug)
        if limit:
            qs = qs[:limit]

        patched = 0
        for log in qs:
            latest = log.replays.order_by("-created_at").first()
            if not latest or not latest.replayed_summary:
                continue
            placeholder = (log.summary or "").strip().lower() in PLACEHOLDERS
            if placeholder or latest.reflection_score >= 0.5:
                log.summary = latest.replayed_summary
                note = f"Patched via Ω.9.52 ({latest.id})"
                if log.insights:
                    if note not in log.insights:
                        log.insights += f"\n{note}"
                else:
                    log.insights = note
                log.save(update_fields=["summary", "insights"])
                latest.drift_reason = "patched"
                latest.save(update_fields=["drift_reason"])
                patched += 1
        self.stdout.write(self.style.SUCCESS(f"{patched} summaries patched"))
