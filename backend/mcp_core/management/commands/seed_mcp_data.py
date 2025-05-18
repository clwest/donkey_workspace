import random
from django.core.management.base import BaseCommand
from mcp_core.models import MemoryContext, Plan, Task,  ActionLog, Tag
from agents.models import Agent
from uuid import uuid4

class Command(BaseCommand):
    help = "Seed basic MCP Core data for testing reflections, plans, tasks."

    def handle(self, *args, **kwargs):
        # Create a Reflection Agent
        reflection_agent, created = Agent.objects.get_or_create(
            name="Reflection Bot 1.0",
            agent_type="ai",
            defaults={"specialty": "Memory Reflection"},
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Created agent: {reflection_agent.name}")
            )
        else:
            self.stdout.write(f"Agent already exists: {reflection_agent.name}")

        # Create test Memories
        memories_data = [
            "Agent performance dipped when memory chains grew too large.",
            "User engagement rose after story personalization improved.",
            "Delay detected between task creation and task completion.",
            "Error rates increased when operating over 100 simultaneous tasks.",
            "Plan execution speed improved by 20% after priority tagging.",
        ]

        memory_objects = []
        for content in memories_data:
            memory, created = MemoryContext.objects.get_or_create(
                content=content,
                defaults={
                    "target_object_id": str(uuid4()),
                    "important": True,
                    "category": "reflection_test",
                },
            )

            if created:
                tag_names = ["seed", "test"]
                tags = Tag.objects.filter(name__in=tag_names)
                memory.tags.set(tags)

            memory_objects.append(memory)
            self.stdout.write(f"✅ Seeded memory: {content[:50]}...")

        # Create test Plans
        plans_data = [
            (
                "Optimize Memory Chain Management",
                "Refactor chain growth rules and pruning strategies.",
            ),
            (
                "Enhance Task Feedback Loops",
                "Improve user feedback on task status and completion.",
            ),
        ]

        plan_objects = []
        for title, description in plans_data:
            plan, created = Plan.objects.get_or_create(
                title=title, defaults={"description": description}
            )
            plan_objects.append(plan)
            self.stdout.write(f"Seeded plan: {title}")

        # Create test Tasks linked to Plans
        tasks_data = [
            ("Implement chain pruning algorithm", 0),
            ("Create task aging and resurfacing system", 1),
            ("Benchmark reflection memory costs", 0),
            ("Automate task feedback status updates", 1),
            ("Integrate task urgency scoring system", 1),
        ]

        for task_title, plan_index in tasks_data:
            task, created = Task.objects.get_or_create(
                title=task_title,
                defaults={
                    "description": f"Auto-seeded task: {task_title}",
                    "plan": plan_objects[plan_index],
                    "status": "open",
                },
            )
            self.stdout.write(f"Seeded task: {task_title}")

        # Optionally, create some ActionLogs
        ActionLog.objects.create(
            action_type="create",
            description="Seeded initial plans and memories",
            related_agent=reflection_agent,
        )
        self.stdout.write(self.style.SUCCESS("Seeded initial ActionLog."))

        self.stdout.write(self.style.SUCCESS("✅ MCP Core seeding complete!"))
