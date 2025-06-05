from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from memory.models import RAGGroundingLog, MemoryEntry
from mcp_core.models import Tag

class Command(BaseCommand):
    """Tag memories near RAG fallbacks with glossary_insight."""

    help = "Attach glossary_insight tag to memories around fallback events"

    def handle(self, *args, **options):
        tag, _ = Tag.objects.get_or_create(slug="glossary_insight", defaults={"name": "glossary_insight"})
        count = 0
        for log in RAGGroundingLog.objects.exclude(fallback_reason__isnull=True):
            start = log.created_at - timedelta(minutes=5)
            end = log.created_at + timedelta(minutes=5)
            mems = MemoryEntry.objects.filter(assistant=log.assistant, created_at__range=(start, end))
            for m in mems:
                if not m.tags.filter(id=tag.id).exists():
                    m.tags.add(tag)
                    count += 1
        self.stdout.write(f"Tagged {count} memories")
