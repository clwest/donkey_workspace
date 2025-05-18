from django.core.management.base import BaseCommand
from assistants.models import AssistantThoughtLog


class Command(BaseCommand):
    help = "Fix mismatched role/thought_type on AssistantThoughtLog"

    def handle(self, *args, **kwargs):
        fixed = 0

        for log in AssistantThoughtLog.objects.all():
            if log.thought_type == "user" and log.role != "user":
                log.role = "user"
                log.save()
                fixed += 1
            elif (
                log.thought_type in ["generated", "cot", "planning", "reflection"]
                and log.role != "assistant"
            ):
                log.role = "assistant"
                log.save()
                fixed += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ Fixed {fixed} inconsistent thought logs.")
        )
