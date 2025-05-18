# mcp_core/management/commands/fix_missing_titles.py

from django.core.management.base import BaseCommand
from mcp_core.models import ReflectionLog
from agents.utils.agent_reflection_engine import AgentReflectionEngine


class Command(BaseCommand):
    help = "Fix reflections missing a title by generating smart titles. Supports --preview mode."

    def add_arguments(self, parser):
        parser.add_argument(
            "--preview",
            action="store_true",
            help="Preview changes without saving.",
        )

    def handle(self, *args, **options):
        agent = AgentReflectionEngine()
        preview = options["preview"]

        reflections = ReflectionLog.objects.filter(
            title__isnull=True
        ) | ReflectionLog.objects.filter(title="")
        total = reflections.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS("✅ No reflections missing titles."))
            return

        fixed = 0

        for reflection in reflections:
            memories = reflection.related_memories.all()
            if not memories.exists():
                continue

            reflection_data = agent.get_structured_reflection(memories)
            new_title = reflection_data.get("title", "Reflection")
            new_summary = reflection_data.get("summary", reflection.summary or "")

            if preview:
                self.stdout.write(
                    self.style.NOTICE(
                        f"Would fix Reflection ID {reflection.id}:\n"
                        f"- New Title: {new_title}\n"
                        f"- New Summary: {new_summary[:100]}...\n"
                    )
                )
            else:
                reflection.title = new_title
                reflection.summary = new_summary
                reflection.save()
                fixed += 1

        if preview:
            self.stdout.write(
                self.style.WARNING(
                    f"👀 Previewed {total} reflections. No changes saved."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"🛠️ Fixed titles for {fixed} reflections!")
            )
