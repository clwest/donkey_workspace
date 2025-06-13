from django.core.management.base import BaseCommand
from assistants.models import Badge


class Command(BaseCommand):
    """Seed default assistant badges."""

    help = "Seed default assistant badges"

    def handle(self, *args, **options):
        badges = [
            ("reflection_ready", "Reflection Ready", None),
            ("prompt_helper", "Prompt Helper", None),
            ("memory_archivist", "Memory Archivist", None),
            ("cli_runner", "CLI Runner", "cli_runs>=5"),
            ("self_repairing", "Self Repairing", "cli_repairs>=1"),
        ]

        for slug, label, criteria in badges:
            _, created = Badge.objects.get_or_create(
                slug=slug, defaults={"label": label, "criteria": criteria or ""}
            )
            if created:
                self.stdout.write(f"✅ Created badge: {slug}")
            else:
                self.stdout.write(f"✔️  Already exists: {slug}")

        self.stdout.write(self.style.SUCCESS("✅ Badge seeding complete."))
