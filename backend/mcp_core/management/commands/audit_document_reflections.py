from django.core.management.base import BaseCommand
from intel_core.models import Document
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from memory.models import MemoryEntry
from assistants.models.reflection import AssistantReflectionLog

class Command(BaseCommand):
    help = "Audit documents for reflection logs and anchors"

    def add_arguments(self, parser):
        parser.add_argument("--fix", action="store_true", help="Run repair actions")

    def handle(self, *args, **opts):
        fix = opts.get("fix", False)
        missing = 0
        for doc in Document.objects.all():
            mem_count = MemoryEntry.objects.filter(document=doc).count()
            ref_count = AssistantReflectionLog.objects.filter(document=doc).count()
            if mem_count == 0 or ref_count == 0:
                self.stdout.write(f"{doc.title}: memories={mem_count} reflections={ref_count}")
                missing += 1
                if fix:
                    assistant = AssistantReflectionEngine.get_reflection_assistant()
                    engine = AssistantReflectionEngine(assistant)
                    engine.reflect_on_document(doc)
        self.stdout.write(self.style.SUCCESS(f"Checked {Document.objects.count()} documents, {missing} missing"))
