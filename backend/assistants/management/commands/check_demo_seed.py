from django.core.management.base import BaseCommand
from django.core.management import call_command
from assistants.models import Assistant
from assistants.utils.starter_chat import seed_chat_starter_memory

EXPECTED = ["prompt-pal", "reflection-sage", "memory-weaver"]

class Command(BaseCommand):
    help = "Ensure demo assistants and starter chats exist"

    def handle(self, *args, **options):
        existing = {a.demo_slug: a for a in Assistant.objects.filter(is_demo=True)}
        missing = [slug for slug in EXPECTED if slug not in existing]

        if missing:
            call_command("seed_demo_assistants")
            existing = {a.demo_slug: a for a in Assistant.objects.filter(is_demo=True)}

        for slug in EXPECTED:
            if slug not in existing:
                self.stdout.write(self.style.ERROR(f"✖ {slug} missing"))
            else:
                self.stdout.write(self.style.SUCCESS(f"✔ {slug}"))

        for demo in existing.values():
            if not demo.memories.exists():
                seed_chat_starter_memory(demo)
            updated = demo.updated_at.strftime("%Y-%m-%d %H:%M")
            count = demo.memories.count()
            self.stdout.write(f"{demo.demo_slug} | {updated} | {count} memories")
