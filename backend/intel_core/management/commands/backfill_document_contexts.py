from django.core.management.base import BaseCommand
from intel_core.models import Document
from memory.models import MemoryEntry
from assistants.models import Assistant

class Command(BaseCommand):
    help = "Backfill Document.memory_context based on related assistants or memories"

    def handle(self, *args, **options):
        count = 0
        docs = Document.objects.filter(memory_context__isnull=True)
        for doc in docs:
            context = None
            mem = (
                MemoryEntry.objects.filter(document=doc, context__isnull=False)
                .order_by("-created_at")
                .first()
            )
            if mem:
                context = mem.context
            else:
                a = doc.linked_assistants.first() or doc.assigned_assistants.first()
                if a and a.memory_context:
                    context = a.memory_context
            if context:
                doc.memory_context = context
                doc.save(update_fields=["memory_context"])
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Updated {count} documents"))
