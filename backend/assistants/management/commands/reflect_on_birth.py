from django.core.management.base import BaseCommand
from assistants.models import Assistant, AssistantReflectionLog
from assistants.helpers.logging_helper import reflect_on_birth



class Command(BaseCommand):
    """Generate origin reflections for assistants."""

    help = "Generate origin reflections for assistants"

    def add_arguments(self, parser):
        parser.add_argument(
            "--demo",
            action="store_true",
            help="Only process demo assistants",
        )

    def handle(self, *args, **options):
        demo_only = options.get("demo")
        assistants = (
            Assistant.objects.filter(is_demo=True)
            if demo_only
            else Assistant.objects.all()
        )

        count = 0
        for assistant in assistants:
            exists = AssistantReflectionLog.objects.filter(
                assistant=assistant,
                title="Origin Reflection",
                category="meta",
            ).exists()
            if not exists:
                reflection = reflect_on_birth(assistant)
                if reflection:
                    count += 1
                    self.stdout.write(f"Reflected on: {assistant.name}")

        self.stdout.write(
            self.style.SUCCESS(f"✅ Added {count} origin reflection{'s' if count != 1 else ''}.")
        )
