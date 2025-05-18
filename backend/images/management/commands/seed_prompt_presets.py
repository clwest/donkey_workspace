from django.core.management.base import BaseCommand
from images.models import PromptHelper
from images.helpers.prompt_helpers import prompt_presets
from images.helpers.prompt_categories import PROMPT_CATEGORIES


class Command(BaseCommand):
    help = "Seed prompt presets into the database with categories"

    def handle(self, *args, **options):
        # Build reverse map: style → category
        style_to_category = {}
        for category, styles in PROMPT_CATEGORIES.items():
            for style in styles:
                style_to_category[style] = category

        created_count = 0
        updated_count = 0

        for name, data in prompt_presets.items():
            category = style_to_category.get(name)
            prompt = data.get("prompt", "")
            negative_prompt = data.get("negative_prompt", "")
            description = data.get("description", "")
            tags = data.get("tags", [])

            obj, created = PromptHelper.objects.update_or_create(
                name=name,
                defaults={
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "category": category,
                    "description": description,
                    "tags": tags,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Created: {name}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"🔄 Updated: {name}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSeeding complete. Created: {created_count}, Updated: {updated_count}"
            )
        )
