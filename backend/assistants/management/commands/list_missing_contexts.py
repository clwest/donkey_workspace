from django.core.management.base import BaseCommand
from assistants.models import Assistant


class Command(BaseCommand):
    help = "List assistants without a memory context"

    def handle(self, *args, **options):
        missing = Assistant.objects.filter(memory_context__isnull=True)
        if not missing:
            self.stdout.write(self.style.SUCCESS("All assistants have a memory context."))
            return
        for a in missing:
            self.stdout.write(f"- {a.name} ({a.slug})")
        self.stdout.write(self.style.WARNING(f"{missing.count()} assistants missing contexts"))
