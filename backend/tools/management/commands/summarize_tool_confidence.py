from django.core.management.base import BaseCommand
from pathlib import Path
import json

from assistants.models import Assistant
from tools.services.tool_confidence import summarize_tool_confidence


class Command(BaseCommand):
    help = "Aggregate tool confidence snapshots for all assistants"

    def handle(self, *args, **options):
        all_data = {}
        for assistant in Assistant.objects.all():
            all_data[assistant.slug] = summarize_tool_confidence(assistant)
        path = Path(__file__).resolve().parents[3] / "static" / "tool_scores.json"
        path.write_text(json.dumps(all_data, indent=2))
        self.stdout.write(self.style.SUCCESS("Tool confidence summarized"))
