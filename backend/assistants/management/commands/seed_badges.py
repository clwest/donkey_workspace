from django.core.management.base import BaseCommand
from assistants.models import Badge


class Command(BaseCommand):
    """Seed default assistant badges."""

    help = "Seed default assistant badges"

    def handle(self, *args, **options):
        badges = [
            ("reflection_ready", "Reflection Ready"),
            ("prompt_helper", "Prompt Helper"),
            ("memory_archivist", "Memory Archivist"),
        ]

        for slug, label in badges:
            _, created = Badge.objects.get_or_create(slug=slug, defaults={"label": label})
            if created:
                self.stdout.write(f"✅ Created badge: {slug}")
            else:
                self.stdout.write(f"✔️  Already exists: {slug}")

        self.stdout.write(self.style.SUCCESS("✅ Badge seeding complete."))
