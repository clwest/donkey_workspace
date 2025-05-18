# assistants/management/commands/clear_thoughts.py

from django.core.management.base import BaseCommand
from assistants.models import AssistantThoughtLog


class Command(BaseCommand):
    help = "🧹 Clears all AssistantThoughtLog entries (careful!)"

    def handle(self, *args, **kwargs):
        count = AssistantThoughtLog.objects.count()

        if count == 0:
            self.stdout.write(self.style.WARNING("⚠️ No thoughts found to clear."))
            return

        AssistantThoughtLog.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(f"🧹 Cleared {count} Assistant Thought entries!")
        )
