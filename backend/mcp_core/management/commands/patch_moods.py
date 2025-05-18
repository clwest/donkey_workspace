from django.core.management.base import BaseCommand
from mcp_core.models import ReflectionLog
from agents.utils.agent_reflection_engine import AgentReflectionEngine


class Command(BaseCommand):
    help = "Patch missing moods in existing reflections."

    def handle(self, *args, **kwargs):
        agent = AgentReflectionEngine()

        reflections = ReflectionLog.objects.filter(mood__isnull=True)

        if not reflections.exists():
            self.stdout.write(self.style.SUCCESS("✅ No missing moods detected."))
            return

        self.stdout.write(
            self.style.WARNING(
                f"⚡ Found {reflections.count()} reflections without mood. Updating..."
            )
        )

        for reflection in reflections:
            mood = agent.analyze_mood(reflection.summary or "")
            reflection.mood = mood
            reflection.save()

        self.stdout.write(self.style.SUCCESS("✅ Mood patch complete! 🎉"))
