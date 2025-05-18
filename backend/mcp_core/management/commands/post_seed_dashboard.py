# mcp_core/management/commands/check_post_seed_status.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.contenttypes.models import ContentType

from prompts.models import Prompt
from memory.models import MemoryEntry
from embeddings.models import Embedding


class Command(BaseCommand):
    help = "Post-seed system health dashboard"

    def handle(self, *args, **options):
        now = timezone.now()
        recent_threshold = now - timedelta(minutes=5)

        def check_model(label: str, model):
            ct = ContentType.objects.get_for_model(model)
            field = content_field_name(model)
            total = model.objects.count()
            with_content = (
                model.objects.exclude(**{f"{field}__isnull": True})
                .exclude(**{field: ""})
                .count()
            )
            embedded = Embedding.objects.filter(content_type=ct).count()

            print(f"📦 {label}")
            print(f"   Total:        {total}")
            print(f"   With content: {with_content}")
            print(f"   Embedded:     {embedded}\n")

        def content_field_name(model):
            # Customize per model if needed
            if model == Prompt:
                return "content"
            elif model == MemoryEntry:
                return "event"
            return "content"  # default fallback

        print("🧭 Post-Seed System Health Check\n")

        check_model("Prompts", Prompt)
        check_model("Memory Entries", MemoryEntry)

        recent_embeddings = Embedding.objects.filter(
            created_at__gte=recent_threshold
        ).count()

        print("📦 Recent Embeddings")
        print(f"   🕒 Last 5 min: {recent_embeddings} embeddings created\n")

        print("✅ Done!")
