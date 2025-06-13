from django.core.management.base import BaseCommand
from assistants.models import Assistant
from assistants.models.tooling import AssistantTool, AssistantToolAssignment
from assistants.utils.assistant_reflection_engine import reflect_on_tools


class Command(BaseCommand):
    help = "Auto assign available tools to all assistants"

    def handle(self, *args, **options):
        tools = list(AssistantTool.objects.all())
        if not tools:
            self.stdout.write(self.style.WARNING("No assistant tools defined"))
            return

        for assistant in Assistant.objects.all():
            created = 0
            for tool in tools:
                assign, new = AssistantToolAssignment.objects.get_or_create(
                    assistant=assistant,
                    tool=tool,
                    defaults={"reason": "auto", "confidence_score": 0.5},
                )
                if new:
                    created += 1
            if created:
                self.stdout.write(f"{assistant.slug}: assigned {created} tools")
                reflect_on_tools(assistant)
        self.stdout.write(self.style.SUCCESS("Tool assignment complete"))
