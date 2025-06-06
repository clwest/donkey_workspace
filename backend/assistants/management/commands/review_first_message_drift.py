from django.core.management.base import BaseCommand
from django.db.models import Count, Avg
from assistants.models import Assistant
from assistants.models.assistant import ChatIntentDriftLog
from assistants.models.glossary import SuggestionLog


class Command(BaseCommand):
    help = "Review first message drift logs and create glossary suggestions"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Slug of assistant to review")
        parser.add_argument("--threshold", type=float, default=0.6)

    def handle(self, *args, **options):
        slug = options.get("assistant")
        threshold = options.get("threshold")
        qs = Assistant.objects.all()
        if slug:
            qs = qs.filter(slug=slug)
        for assistant in qs:
            logs = ChatIntentDriftLog.objects.filter(
                assistant=assistant,
                drift_score__gte=threshold,
            )
            miss_counts = {}
            for log in logs:
                for miss in log.glossary_misses:
                    miss_counts[miss] = miss_counts.get(miss, 0) + 1
            for anchor, count in miss_counts.items():
                if count >= 3:
                    SuggestionLog.objects.get_or_create(
                        assistant=assistant,
                        anchor_slug=anchor,
                        trigger_type="first_message_drift",
                        defaults={
                            "suggested_action": "mutate",
                            "score": count,
                        },
                    )
            self.stdout.write(self.style.SUCCESS(f"Reviewed {assistant.slug}"))
