from django.core.management.base import BaseCommand
from agents.models import Agent, SwarmMemoryEntry
from assistants.models import AssistantProject


class Command(BaseCommand):
    help = "Seed demo SwarmMemoryEntry records"

    def handle(self, *args, **options):
        agent = Agent.objects.first()
        project = AssistantProject.objects.first()

        entries = [
            {
                "title": "Cluster Formation",
                "content": "Initial demo cluster assembled for testing.",
            },
            {
                "title": "Training Session Completed",
                "content": "Agents finished first collective training cycle.",
            },
            {
                "title": "Project Milestone Achieved",
                "content": "Demo project reached its first milestone.",
            },
        ]

        for entry_data in entries:
            entry = SwarmMemoryEntry.objects.create(**entry_data)
            if agent:
                entry.linked_agents.add(agent)
            if project:
                entry.linked_projects.add(project)
            self.stdout.write(f"Added memory: {entry.title}")

        self.stdout.write(self.style.SUCCESS("Swarm memory seeded."))
