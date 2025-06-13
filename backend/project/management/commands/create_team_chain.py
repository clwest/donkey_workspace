from django.core.management.base import BaseCommand
from assistants.models import Assistant, AssistantMemoryChain
from assistants.utils.resolve import resolve_assistant
from project.models import Project


class Command(BaseCommand):
    help = "Create a team memory chain for a project"

    def add_arguments(self, parser):
        parser.add_argument("--project", required=True)
        parser.add_argument("--assistants", default="")

    def handle(self, *args, **options):
        project = Project.objects.get(title=options["project"])
        chain = AssistantMemoryChain.objects.create(
            title=f"{project.title} Team Chain",
            project=project,
            linked_project=project,
            is_team_chain=True,
        )
        slugs = [s for s in options["assistants"].split(",") if s]
        for slug in slugs:
            a = resolve_assistant(slug)
            if a:
                chain.team_members.add(a)
                project.team.add(a)
            else:
                self.stderr.write(self.style.ERROR(f"Assistant {slug} not found"))
        project.team_chain = chain
        project.save()
        self.stdout.write(self.style.SUCCESS(f"✅ Created team chain {chain.title}"))
