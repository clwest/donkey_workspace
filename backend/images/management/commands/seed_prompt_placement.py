from django.core.management.base import BaseCommand
from images.models import PromptPlacement

PROMPT_PLACEMENTS = [
    {
        "name": "Image Style Prompt",
        "prompt_type": "image",
        "placement": "append",
        "description": "Appends visual style details to the end of the image generation prompt.",
    },
    {
        "name": "Narration Prompt",
        "prompt_type": "narration",
        "placement": "prefix",
        "description": "Adds tone and character voice guidance at the beginning of narration prompts.",
    },
    {
        "name": "Voice Prompt (TTS)",
        "prompt_type": "voice",
        "placement": "replace",
        "description": "Replaces default TTS style with selected voice style instructions.",
    },
    {
        "name": "Video Scene Prompt",
        "prompt_type": "video",
        "placement": "append",
        "description": "Appends cinematic instructions to generated video scene prompts.",
    },
    {
        "name": "Style Modifier",
        "prompt_type": "style",
        "placement": "append",
        "description": "Used to modify base prompts with selected visual style presets.",
    },
    {
        "name": "Scene Descriptor",
        "prompt_type": "scene",
        "placement": "prefix",
        "description": "Adds descriptive scene setting to enhance prompt grounding.",
    },
]


class Command(BaseCommand):
    help = "Seed default PromptPlacement entries"

    def handle(self, *args, **options):
        created, updated = 0, 0

        for item in PROMPT_PLACEMENTS:
            obj, was_created = PromptPlacement.objects.update_or_create(
                name=item["name"],
                defaults={
                    "prompt_type": item["prompt_type"],
                    "placement": item["placement"],
                    "description": item.get("description", ""),
                    "is_enabled": True,
                },
            )

            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Created: {obj.name}"))
            else:
                updated += 1
                self.stdout.write(self.style.WARNING(f"🔄 Updated: {obj.name}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSeeding complete. Created: {created}, Updated: {updated}"
            )
        )
