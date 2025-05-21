from django.core.management.base import BaseCommand
from agents.models import MissionArchetype
from assistants.models import Assistant


ARCHETYPES = [
    {
        "name": "Prompt Engineering Lab",
        "description": "Experts dedicated to refining and testing prompts.",
        "core_skills": ["prompt design", "evaluation"],
        "preferred_cluster_structure": {"size": 3, "roles": ["lead", "tester", "reviewer"]},
    },
    {
        "name": "Tool Builder Task Force",
        "description": "Rapid development of helper utilities and tools.",
        "core_skills": ["python", "api integration"],
        "preferred_cluster_structure": {"size": 4, "roles": ["architect", "developer", "qa"]},
    },
    {
        "name": "LangChain Evaluation Squad",
        "description": "Evaluates and benchmarks LangChain pipelines.",
        "core_skills": ["langchain", "benchmarking"],
        "preferred_cluster_structure": {"size": 2, "roles": ["researcher", "analyst"]},
    },
]


class Command(BaseCommand):
    help = "Seed MissionArchetype examples"

    def handle(self, *args, **options):
        creator = Assistant.objects.first()
        for data in ARCHETYPES:
            arch, _ = MissionArchetype.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "core_skills": data["core_skills"],
                    "preferred_cluster_structure": data["preferred_cluster_structure"],
                    "created_by": creator,
                },
            )
            self.stdout.write(f"Archetype added: {arch.name}")

        self.stdout.write(self.style.SUCCESS("Mission archetypes seeded."))
