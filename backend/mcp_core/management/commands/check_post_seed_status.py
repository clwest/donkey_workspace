from django.core.management.base import BaseCommand
from prompts.models import Prompt
from memory.models import MemoryEntry
from embeddings.models import Embedding
from django.utils.timezone import now, timedelta
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = "Prints a dashboard summary of post-seed system health"

    def handle(self, *args, **options):
        print("\n🧭 Post-Seed System Health Check\n")

        def content_field_name(model):
            if model == Prompt:
                return "content"
            elif model == MemoryEntry:
                return "event"
            return "content"

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

        check_model("Prompts", Prompt)
        check_model("Memory Entries", MemoryEntry)

        print("📦 Recent Embeddings")
        recent = Embedding.objects.filter(
            created_at__gte=now() - timedelta(minutes=5)
        ).count()
        print(f"   🕒 Last 5 min: {recent} embeddings created\n")

        print("✅ Done!\n")
