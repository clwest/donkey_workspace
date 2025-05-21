from django.core.management.base import BaseCommand
from story.models import NarrativeEvent
from mcp_core.utils.scene_summary import summarize_scene_context


class Command(BaseCommand):
    help = "Generate summaries for recent narrative events without summaries."

    def handle(self, *args, **options):
        events = NarrativeEvent.objects.filter(summary_generated=False).order_by("-timestamp")[:10]
        for event in events:
            try:
                summarize_scene_context(event)
                self.stdout.write(f"✅ Summarized {event.title}")
            except Exception as e:
                self.stderr.write(f"❌ Failed to summarize {event.id}: {e}")

