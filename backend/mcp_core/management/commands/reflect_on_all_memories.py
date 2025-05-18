from django.core.management.base import BaseCommand
from memory.models import MemoryEntry
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from assistants.models import AssistantReflectionLog
from django.utils.timezone import now

class Command(BaseCommand):
    help = "Reflect on all memory entries that have not yet been reflected on."

    def handle(self, *args, **kwargs):
        total = 0
        skipped = 0
        failed = 0

        print("🔍 Searching for memory entries missing reflections...")

        for memory in MemoryEntry.objects.all():
            if AssistantReflectionLog.objects.filter(linked_memory=memory).exists():
                skipped += 1
                continue

            try:
                assistant = memory.assistant or AssistantReflectionEngine.get_reflection_assistant()
                engine = AssistantReflectionEngine(assistant)
                summary = engine.reflect_on_memory(memory)

                AssistantReflectionLog.objects.create(
                    assistant=assistant,
                    linked_memory=memory,
                    summary=summary,
                    title=f"Reflection on memory {memory.id}",
                    mood="neutral",
                    created_at=now(),
                )
                print(f"✅ Reflected on memory {memory.id}")
                total += 1
            except Exception as e:
                print(f"❌ Failed to reflect on memory {memory.id}: {e}")
                failed += 1

        print(f"\\n🧠 Memory reflection complete.")
        print(f"✔️ Reflected: {total}")
        print(f"⏭️ Skipped: {skipped}")
        print(f"❌ Failed: {failed}")