from django.core.management.base import BaseCommand
from agents.models import Agent, AgentTrainingAssignment
from assistants.models import Assistant
from intel_core.models import Document

class Command(BaseCommand):
    help = "Assign random training documents to demo agents"

    def handle(self, *args, **options):
        agents = Agent.objects.filter(is_demo=True)
        if not agents.exists():
            self.stdout.write(self.style.WARNING("No demo agents found."))
            return

        assistant = Assistant.objects.first()
        summary = []
        for agent in agents:
            docs = list(Document.objects.order_by("?")[:3])
            titles = []
            for doc in docs:
                AgentTrainingAssignment.objects.create(
                    agent=agent,
                    document=doc,
                    assistant=assistant,
                )
                titles.append(doc.title)
            summary.append(f"{agent.name}: {', '.join(titles)}")

        self.stdout.write("\n".join(summary))
        self.stdout.write(self.style.SUCCESS("Training assignments seeded."))

