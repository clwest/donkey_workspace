from django.core.management.base import BaseCommand
from assistants.models import Assistant
from memory.utils.glossary_keeper import run_keeper_tasks


class Command(BaseCommand):
    help = "Run the Glossary Keeper drift checks"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=False)

    def handle(self, *args, **options):
        slug = options.get("assistant")
        assistant = None
        if slug:
            try:
                assistant = Assistant.objects.get(slug=slug)
            except Assistant.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Assistant '{slug}' not found"))
                return
        run_keeper_tasks(assistant=assistant)
        self.stdout.write(self.style.SUCCESS("Glossary Keeper run complete"))
