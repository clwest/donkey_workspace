# assistants/management/commands/seed_thoughts.py

from django.core.management.base import BaseCommand
from assistants.models import AssistantThoughtLog
from project.models import Project
from memory.models import MemoryEntry
from django.utils import timezone
import random

SAMPLE_THOUGHTS = [
    "I should prioritize completing urgent tasks before starting new ones.",
    "Our current memory management could be optimized by batching more frequently.",
    "Consider reflecting on recent task failures to extract lessons learned.",
    "Generating daily reflections might help improve performance trends.",
    "Memory linkages between objectives and actions could be improved.",
    "Task prioritization seems slightly misaligned with project goals.",
    "Thinking about restructuring milestones to better match deliverables.",
    "User engagement seems tied to faster feedback cycles.",
]


class Command(BaseCommand):
    help = "🧠 Seeds assistant projects with initial thoughts (optionally linked to memories)."

    def handle(self, *args, **kwargs):
        projects = Project.objects.all()

        if not projects.exists():
            self.stdout.write(
                self.style.WARNING("⚠️ No projects found to seed thoughts for.")
            )
            return

        count = 0
        for project in projects:
            existing_thoughts = AssistantThoughtLog.objects.filter(
                project=project
            ).count()
            if existing_thoughts == 0:
                linked_memories = project.linked_memories.all()

                for _ in range(random.randint(3, 5)):
                    linked_memory = None
                    if (
                        linked_memories.exists() and random.random() < 0.5
                    ):  # 50% chance to link
                        linked_memory = random.choice(linked_memories).memory

                    AssistantThoughtLog.objects.create(
                        project=project,
                        thought=random.choice(SAMPLE_THOUGHTS),
                        linked_memory=linked_memory,
                        created_at=timezone.now(),
                    )
                count += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ Seeded thoughts for {count} projects!")
        )
