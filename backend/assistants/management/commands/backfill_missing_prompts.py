from django.core.management.base import BaseCommand
from assistants.models import Assistant
from prompts.models import Prompt


class Command(BaseCommand):
    help = "Assign generic system prompt to assistants missing one"

    def handle(self, *args, **options):
        generic, _ = Prompt.objects.get_or_create(
            slug="generic",
            defaults={
                "title": "Generic",
                "content": "You are a helpful assistant.",
                "type": "system",
                "source": "fallback",
            },
        )
        count = 0
        for a in Assistant.objects.filter(system_prompt__isnull=True):
            a.system_prompt = generic
            a.save(update_fields=["system_prompt"])
            count += 1
        self.stdout.write(self.style.SUCCESS(f"✅ Updated {count} assistants"))
