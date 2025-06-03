from django.core.management.base import BaseCommand
from assistants.models import Assistant
from mcp_core.models import MemoryContext


class Command(BaseCommand):
    help = "Assign missing memory_contexts to assistants"

    def handle(self, *args, **kwargs):
        count = 0
        for a in Assistant.objects.filter(memory_context__isnull=True):
            ctx = MemoryContext.objects.create(content=f"{a.name} Context")
            a.memory_context = ctx
            a.save(update_fields=["memory_context"])
            count += 1
        self.stdout.write(self.style.SUCCESS(f"✅ Backfilled {count} assistants."))
