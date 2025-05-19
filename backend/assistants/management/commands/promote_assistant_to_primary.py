from django.core.management.base import BaseCommand
from assistants.models import Assistant

class Command(BaseCommand):
    help = "Promote an assistant to be the primary orchestrator"

    def add_arguments(self, parser):
        parser.add_argument("--slug", required=True)

    def handle(self, *args, **options):
        slug = options["slug"]
        try:
            assistant = Assistant.objects.get(slug=slug)
        except Assistant.DoesNotExist:
            self.stderr.write(self.style.ERROR("Assistant not found"))
            return

        Assistant.objects.filter(is_primary=True).update(is_primary=False)
        assistant.is_primary = True
        assistant.save()
        self.stdout.write(self.style.SUCCESS(f"{assistant.name} promoted to primary"))
