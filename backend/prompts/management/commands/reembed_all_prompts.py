from django.core.management.base import BaseCommand
from prompts.models import Prompt
from embeddings.helpers.helpers_processing import generate_embedding
from django.db import transaction


class Command(BaseCommand):
    help = "Regenerate embeddings for all prompts"

    def handle(self, *args, **options):
        total = 0
        failed = 0

        self.stdout.write("🔁 Re-embedding prompts...\n")

        prompts = Prompt.objects.all()

        for prompt in prompts:
            try:
                embedding = generate_embedding(prompt.content)
                if not embedding:
                    raise ValueError("Empty embedding returned.")

                prompt.embedding = embedding
                with transaction.atomic():
                    prompt.save()
                total += 1
                self.stdout.write(f"✅ Embedded: {prompt.title}")
            except Exception as e:
                failed += 1
                self.stderr.write(f"❌ Failed: {prompt.title} — {e}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Re-embedding complete. Total: {total}, Failures: {failed}"
            )
        )
