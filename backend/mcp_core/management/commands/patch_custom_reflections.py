from django.core.management.base import BaseCommand
from mcp_core.models import ReflectionLog
from agents.utils.agent_reflection_engine import AgentReflectionEngine


class Command(BaseCommand):
    help = "Patch incomplete custom reflections: missing title, summary, or LLM reflection."

    def handle(self, *args, **options):
        reflections = ReflectionLog.objects.all()
        agent = AgentReflectionEngine()

        fixed_count = 0

        for reflection in reflections:
            update_needed = False

            # Title patch
            if not reflection.title or reflection.title.strip() == "":
                reflection.title = agent.generate_reflection_title(
                    reflection.raw_summary or reflection.summary or ""
                )
                update_needed = True

            # Raw summary patch
            if not reflection.raw_summary or reflection.raw_summary.strip() == "":
                # fallback: if raw_summary missing, just summarize the related memories
                if reflection.related_memories.exists():
                    raw_summary = agent.summarize_reflection(
                        list(reflection.related_memories.all())
                    )
                    reflection.raw_summary = raw_summary
                    update_needed = True

            # LLM summary patch
            if not reflection.llm_summary or reflection.llm_summary.strip() == "":
                content = reflection.raw_summary or reflection.summary or ""
                if content:
                    llm_summary = agent.get_llm_summary_from_raw_summary(content)
                    reflection.llm_summary = llm_summary
                    update_needed = True

            if update_needed:
                reflection.save()
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Patched Reflection ID {reflection.id}")
                )

                fixed_count += 1

        if fixed_count == 0:
            self.stdout.write(
                self.style.SUCCESS("🎯 No broken reflections found. Database is clean!")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"🛠 Patched {fixed_count} reflections!")
            )
