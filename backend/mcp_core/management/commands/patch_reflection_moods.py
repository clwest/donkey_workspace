# mcp_core/management/commands/patch_reflection_moods.py

from django.core.management.base import BaseCommand
from mcp_core.models import ReflectionLog
from agents.utils.agent_reflection_engine import AgentReflectionEngine


class Command(BaseCommand):
    help = "Analyze and patch missing moods for existing reflections."

    def handle(self, *args, **options):
        agent = AgentReflectionEngine()

        reflections = ReflectionLog.objects.filter(mood__isnull=True)
        self.stdout.write(f"Found {reflections.count()} reflections missing mood.")

        for reflection in reflections:
            if reflection.summary:
                mood = agent.analyze_mood(reflection.summary)
                reflection.mood = mood
                reflection.save()
                self.stdout.write(f"✅ Reflection {reflection.id} mood set to: {mood}")
            else:
                self.stdout.write(
                    f"⚠️ Reflection {reflection.id} missing summary, skipping."
                )
