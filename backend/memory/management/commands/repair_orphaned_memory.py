from django.core.management.base import BaseCommand
from assistants.models import Assistant
from memory.models import MemoryEntry


class Command(BaseCommand):
    """Repair MemoryEntry objects missing a context for demo assistants."""

    help = "Link orphaned memories for demo assistants to their memory context"

    def handle(self, *args, **options):
        total = 0
        demos = Assistant.objects.filter(is_demo=True)
        for assistant in demos:
            context = assistant.memory_context
            if not context:
                continue
            repaired = (
                MemoryEntry.objects.filter(assistant=assistant, context__isnull=True)
                .update(context=context)
            )
            if repaired:
                self.stdout.write(f"{assistant.slug}: {repaired} repaired")
            total += repaired
        self.stdout.write(self.style.SUCCESS(f"Total repaired: {total}"))
