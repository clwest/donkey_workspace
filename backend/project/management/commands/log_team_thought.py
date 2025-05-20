from django.core.management.base import BaseCommand
from assistants.models import Assistant
from memory.models import MemoryEntry
from project.models import Project
from assistants.helpers.team_memory import propagate_memory_to_team_chain


class Command(BaseCommand):
    help = "Log a thought from an assistant to the team chain"

    def add_arguments(self, parser):
        parser.add_argument("--project_id", required=True)
        parser.add_argument("--assistant_slug", required=True)
        parser.add_argument("--thought", required=True)

    def handle(self, *args, **options):
        project = Project.objects.get(id=options["project_id"])
        assistant = Assistant.objects.get(slug=options["assistant_slug"])
        mem = MemoryEntry.objects.create(
            event=options["thought"],
            assistant=assistant,
            related_project=project,
        )
        propagate_memory_to_team_chain(mem)
        self.stdout.write(self.style.SUCCESS("Thought logged"))
