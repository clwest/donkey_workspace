from django.core.management.base import BaseCommand
from assistants.models import Assistant
from assistants.models.reflection import AssistantReflectionLog

class Command(BaseCommand):
    help = "Seed reflection logs for demo assistants"

    def handle(self, *args, **options):
        count = 0
        for assistant in Assistant.objects.filter(is_demo=True):
            for i in range(2):
                AssistantReflectionLog.objects.create(
                    assistant=assistant,
                    title=f"Demo Reflection {i+1}",
                    summary=f"This is a demo reflection {i+1} for {assistant.name}",
                    demo_reflection=True,
                )
                count += 1
        self.stdout.write(self.style.SUCCESS(f"✅ Seeded {count} reflections"))
