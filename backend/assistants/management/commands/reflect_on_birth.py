from django.core.management.base import BaseCommand
from assistants.models import Assistant
from memory.models import MemoryEntry


class Command(BaseCommand):
    """Generate origin reflections for all demo assistants."""

    help = "Reflect on assistant birth (for demo assistants)"

    def handle(self, *args, **options):
        count = 0
        for assistant in Assistant.objects.filter(is_demo=True):
            exists = MemoryEntry.objects.filter(
                assistant=assistant,
                memory_type="reflection",
            ).exists()
            if not exists:
                MemoryEntry.objects.create(
                    assistant=assistant,
                    event=f"{assistant.name} was created to help users with {assistant.specialty}.",
                    memory_type="reflection",
                    is_demo=True,
                )
                count += 1
                self.stdout.write(f"Reflected on: {assistant.name}")

        self.stdout.write(self.style.SUCCESS(f"✅ Added {count} demo reflections."))
