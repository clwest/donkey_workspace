from django.core.management.base import BaseCommand
from memory.models import MemoryEntry
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = "Prune old and low-importance memories."

    def handle(self, *args, **options):
        threshold_days = 30  # memories older than 30 days
        importance_threshold = 5  # importance < 5 gets deleted

        cutoff_date = timezone.now() - timedelta(days=threshold_days)

        # Find candidates
        old_memories = MemoryEntry.objects.filter(
            created_at__lt=cutoff_date, importance__lt=importance_threshold
        )

        count = old_memories.count()

        # Delete them
        old_memories.delete()

        self.stdout.write(
            self.style.SUCCESS(f"🧹 Garbage Collector: Deleted {count} old memories.")
        )
