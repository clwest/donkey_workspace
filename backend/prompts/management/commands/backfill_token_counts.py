from django.core.management.base import BaseCommand
from prompts.models import Prompt
from prompts.utils.token_helpers import (
    count_tokens,
)  # Adjust this import to your actual token counter


class Command(BaseCommand):
    help = "Backfill token_count for all prompts"

    def handle(self, *args, **kwargs):
        updated = 0
        for prompt in Prompt.objects.all():
            if prompt.token_count == 0:
                prompt.token_count = count_tokens(prompt.content)
                prompt.save()
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Backfilled {updated} prompts"))
