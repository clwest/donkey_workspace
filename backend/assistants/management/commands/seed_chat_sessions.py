from django.core.management.base import BaseCommand
from assistants.models import Assistant
from memory.models import MemoryEntry


class Command(BaseCommand):
    """Seed starter chat memory for assistants."""

    help = "Seed starter chat messages for assistants"

    def add_arguments(self, parser):
        parser.add_argument(
            "--demo",
            action="store_true",
            help="Only seed demo assistants",
        )

    def handle(self, *args, **options):
        demo_only = options["demo"]
        assistants = (
            Assistant.objects.filter(is_demo=True)
            if demo_only
            else Assistant.objects.all()
        )
        seeded = 0

        for assistant in assistants:
            exists = MemoryEntry.objects.filter(
                assistant=assistant,
                is_demo=True,
                memory_type="chat",
            ).exists()
            if not exists:
                MemoryEntry.objects.create(
                    assistant=assistant,
                    event="Hi! I’m here to help you explore my skills. Try asking me anything!",
                    is_demo=True,
                    memory_type="chat",
                )
                seeded += 1
                self.stdout.write(f"Seeded chat for: {assistant.name}")

        self.stdout.write(self.style.SUCCESS(f"✅ Seeded {seeded} assistant chats."))
