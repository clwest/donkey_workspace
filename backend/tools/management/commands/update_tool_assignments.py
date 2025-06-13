from django.core.management.base import BaseCommand
from django.utils import timezone

from assistants.models.tooling import AssistantToolAssignment
from assistants.models import Assistant
from tools.services.tool_confidence import summarize_tool_confidence


class Command(BaseCommand):
    help = "Drop low-confidence tools and refresh assignment scores"

    def add_arguments(self, parser):
        parser.add_argument("--threshold", type=float, default=0.3)

    def handle(self, *args, **options):
        threshold = options["threshold"]
        for assistant in Assistant.objects.all():
            scores = summarize_tool_confidence(assistant)
            for s in scores:
                try:
                    assign = AssistantToolAssignment.objects.get(
                        assistant=assistant, tool__slug=s["tool"]
                    )
                except AssistantToolAssignment.DoesNotExist:
                    continue
                assign.confidence_score = s["avg_confidence"]
                assign.last_used_at = timezone.now() if s["usage_count"] else assign.last_used_at
                assign.save(update_fields=["confidence_score", "last_used_at"])
                if s["avg_confidence"] < threshold:
                    assign.delete()
                    self.stdout.write(f"Dropped {s['tool']} from {assistant.slug}")
        self.stdout.write(self.style.SUCCESS("Assignments updated"))
