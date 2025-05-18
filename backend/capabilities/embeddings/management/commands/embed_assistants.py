from django.core.management.base import BaseCommand
from assistants.models import Assistant
from embeddings.helpers.helpers_io import get_embedding_for_text


class Command(BaseCommand):
    help = "Generate and store OpenAI embeddings for each Assistant description."

    def handle(self, *args, **options):
        assistants = Assistant.objects.all()
        embedded = 0
        skipped = 0
        failed = 0

        for a in assistants:
            if a.embedding:
                self.stdout.write(f"⏭️ Skipping already embedded assistant: {a.name}")
                skipped += 1
                continue

            try:
                text = f"{a.name}: {a.description or ''}"
                a.embedding = get_embedding_for_text(text)
                a.save()
                self.stdout.write(f"✅ Embedded: {a.name}")
                embedded += 1
            except Exception as e:
                self.stderr.write(f"❌ Failed to embed {a.name}: {e}")
                failed += 1

        self.stdout.write(self.style.SUCCESS("✅ Assistant embedding complete."))
        self.stdout.write(f"✔️ Embedded: {embedded}")
        self.stdout.write(f"⏭️ Skipped: {skipped}")
        self.stdout.write(f"❌ Failed: {failed}")
