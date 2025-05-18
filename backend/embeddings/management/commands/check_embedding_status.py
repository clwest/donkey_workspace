# embeddings/management/commands/check_embedding_status.py
from django.core.management.base import BaseCommand
from prompts.models import Prompt
from memory.models import MemoryEntry
from embeddings.models import Embedding
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta


class Command(BaseCommand):
    help = "Check the number of embedded records across models"

    def handle(self, *args, **kwargs):
        self.stdout.write("📊 Checking embedding status...")

        self.check_model(Prompt, "Prompt")
        self.check_model(MemoryEntry, "MemoryEntry")

        now = timezone.now()
        five_minutes_ago = now - timedelta(minutes=5)

        recent = Embedding.objects.filter(created_at__gte=five_minutes_ago).count()
        self.stdout.write(f"\n🕒 Embeddings created in last 5 minutes: {recent}\n")
        self.stdout.write("✅ Embedding status check complete!")

    def check_model(self, model_class, name):
        content_type = ContentType.objects.get_for_model(model_class)
        embedded = Embedding.objects.filter(content_type=content_type).count()
        total = model_class.objects.count()
        print(f"{name}: Embedded {embedded} of {total}")
