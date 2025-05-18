from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Seeds all prompt helpers and prompt placements into the database"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("🌱 Seeding Prompt Helpers..."))
        call_command("seed_prompt_presets")  # Not seed_prompt_helpers

        self.stdout.write(self.style.MIGRATE_HEADING("🌿 Seeding Prompt Placements..."))
        call_command("seed_prompt_placement")

        self.stdout.write(self.style.SUCCESS("✅ All prompts seeded successfully."))
