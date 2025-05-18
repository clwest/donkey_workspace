from django.core.management.base import BaseCommand
from memory.models import MemoryEntry
from assistants.models import Assistant
from django.utils import timezone
import random

EXAMPLE_EVENTS = [
    "Started building the assistant reflection system.",
    "User expressed frustration with memory seeding.",
    "Successfully embedded 20 prompts using OpenAI.",
    "Revisited the assistant dashboard UI.",
    "Refactored the embeddings logic.",
    "Debugged the post-seed check script.",
    "Improved clarity of thought logging.",
    "Added support for assistant projects.",
    "Investigated Celery task failures.",
    "Clarified naming between MemoryContext and MemoryEntry.",
]


class Command(BaseCommand):
    help = "Seed memory entries linked to DonkGPT"

    def handle(self, *args, **options):
        assistant = Assistant.objects.get(slug="donkgpt")
        MemoryEntry.objects.filter(assistant=assistant).delete()

        for event in EXAMPLE_EVENTS:
            entry = MemoryEntry.objects.create(
                assistant=assistant,
                event=event,
                emotion=random.choice(
                    ["curious", "frustrated", "focused", "energized"]
                ),
                importance=random.randint(1, 10),
                source_role="assistant",
            )
            print("🧠 Seeded:", entry.event[:60])

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Seeded {len(EXAMPLE_EVENTS)} memory entries for {assistant.name}!"
            )
        )
