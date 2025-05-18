from django.core.management.base import BaseCommand
from mcp_core.models import ReflectionLog
from agents.utils.agent_reflection_engine import AgentReflectionEngine


class Command(BaseCommand):
    help = "Patch reflections missing llm_summary."

    def handle(self, *args, **kwargs):
        agent = AgentReflectionEngine()
        reflections = ReflectionLog.objects.filter(llm_summary__isnull=True)

        self.stdout.write(
            f"Found {reflections.count()} reflections missing LLM summary..."
        )

        for reflection in reflections:
            if not reflection.raw_summary:
                continue  # 👈 Skip ones with missing raw_summary

            fake_memories = []
            for line in reflection.raw_summary.split("\n"):
                if line.strip().startswith("• "):
                    content = line.replace("• ", "").strip()

                    class FakeMemory:
                        def __init__(self, content):
                            self.content = content

                    fake_memories.append(FakeMemory(content))

            if fake_memories:
                llm_summary = agent.get_llm_summary(fake_memories)
                reflection.llm_summary = llm_summary
                reflection.save()
                self.stdout.write(f"✅ Patched reflection {reflection.id}")
