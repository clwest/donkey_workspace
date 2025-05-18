from django.core.management.base import BaseCommand
from prompts.models import Prompt
from memory.models import MemoryEntry
from embeddings.models import Embedding
from django.utils.timezone import now, timedelta


class Command(BaseCommand):
    help = "Prints a dashboard summary of post-seed system health"

    def handle(self, *args, **options):
        print("\n🧭 Post-Seed System Health Check\n")

        def section(label):
            print(f"📦 {label}")

        def check_model(name, model):
            total = model.objects.count()
            with_content = (
                model.objects.exclude(event__isnull=True)
                .exclude(event__exact="")
                .count()
                if name == "MemoryEntry"
                else model.objects.exclude(content__isnull=True)
                .exclude(content__exact="")
                .count()
            )
            embedded = Embedding.objects.filter(content_type=name.lower()).count()
            print(f"   Total:       {total}")
            print(f"   With content:{with_content}")
            print(f"   Embedded:    {embedded}\n")

        section("Prompts")
        check_model("Prompt", Prompt)

        section("Memory Entries")
        check_model("MemoryEntry", MemoryEntry)

        section("Recent Embeddings")
        recent = Embedding.objects.filter(
            created_at__gte=now() - timedelta(minutes=5)
        ).count()
        print(f"   🕒 Last 5 min: {recent} embeddings created\n")

        print("✅ Done!\n")
