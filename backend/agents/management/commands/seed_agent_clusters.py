from django.core.management.base import BaseCommand
from agents.models import Agent, AgentCluster
from assistants.models import AssistantProject, Assistant
import random

CLUSTERS = [
    {
        "name": "Data Extraction Squad",
        "purpose": "Handles all data ingestion and extraction tasks",
    },
    {
        "name": "Planning + Coordination",
        "purpose": "Coordinates project timelines and objectives",
    },
    {
        "name": "LangChain Tool Experts",
        "purpose": "Specialists in LangChain integrations and tooling",
    },
]

class Command(BaseCommand):
    help = "Seed demo AgentClusters with agents"

    def handle(self, *args, **options):
        assistant = Assistant.objects.first()
        if not assistant:
            self.stdout.write(self.style.ERROR("No assistant found."))
            return

        project, _ = AssistantProject.objects.get_or_create(
            assistant=assistant,
            title="Demo Cluster Project",
            defaults={"goal": "Experiment with agent clusters"},
        )

        agents = list(Agent.objects.all())
        if not agents:
            self.stdout.write(self.style.WARNING("No agents available to assign."))
            return
        random.shuffle(agents)
        idx = 0

        for entry in CLUSTERS:
            cluster, _ = AgentCluster.objects.get_or_create(
                name=entry["name"],
                defaults={"purpose": entry["purpose"], "project": project},
            )
            cluster.agents.clear()
            assign = agents[idx : idx + 5]
            cluster.agents.add(*assign)
            cluster.save()
            idx += 5
            agent_names = ", ".join(a.name for a in assign)
            self.stdout.write(
                f"\n✅ {cluster.name}\nPurpose: {cluster.purpose}\nAgents: {agent_names}"
            )

