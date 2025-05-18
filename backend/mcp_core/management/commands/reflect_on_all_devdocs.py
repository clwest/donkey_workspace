from django.core.management.base import BaseCommand
from mcp_core.models import DevDoc
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine


class Command(BaseCommand):
    help = "Reflect on all DevDocs individually and save insights."

    def handle(self, *args, **options):
        docs = DevDoc.objects.all()
        if not docs.exists():
            self.stdout.write(self.style.WARNING("No DevDocs found."))
            return

        assistant = AssistantReflectionEngine.get_reflection_assistant()
        engine = AssistantReflectionEngine(assistant)
        reflected = 0
        skipped = 0
        failed = 0

        for doc in docs:
            if doc.reflected_at:
                skipped += 1
                continue

            try:
                memory = engine.reflect_on_document(doc)
                if memory:
                    reflected += 1
                    self.stdout.write(self.style.SUCCESS(f"✅ Reflected on: {doc.title}"))
                else:
                    failed += 1
                    self.stdout.write(self.style.WARNING(f"⚠️ No memory returned for: {doc.title}"))
            except Exception as e:
                failed += 1
                self.stderr.write(f"❌ Failed on {doc.title}: {str(e)}")

        self.stdout.write(self.style.SUCCESS("✅ DevDoc reflection complete."))
        self.stdout.write(f"✔️ Reflected: {reflected}")
        self.stdout.write(f"⏭️ Skipped: {skipped}")
        self.stdout.write(f"❌ Failed: {failed}")