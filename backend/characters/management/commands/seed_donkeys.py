"""
Seed reusable Donkey characters into the database.

Usage:
    python manage.py seed_donkeys [--with-images]
"""

import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from characters.models import (
    CharacterProfile,
    CharacterStyle,
    CharacterTag,
)
from images.models import PromptHelper

logger = logging.getLogger("characters")

DONKEYS = [
    {
        "name": "DJ Donk-Drop",
        "description": "A party‑loving donkey with rhythmic hoof beats.",
        "personality_traits": ["energetic", "musical", "sociable"],
        "backstory": (
            "Born on the neon‑lit plains of Festa Valley, DJ Donk‑Drop discovered beats were more powerful than brays. "
            "With turntables salvaged from ancient festivals, he spins tracks that unite creatures across the land."
        ),
        "tags": ["adventurer", "musician", "goofy"],
    },
    {
        "name": "Detective Donko",
        "description": "A sleuthing donkey with a nose for clues.",
        "personality_traits": ["observant", "curious", "methodical"],
        "backstory": (
            "In the foggy streets of Brayford, Detective Donko solved mysteries no one dared approach. "
            "Armed with a magnifying glass and an insatiable curiosity, he cracks cases with unerring precision."
        ),
        "tags": ["detective", "mystery", "noir"],
    },
    {
        "name": "Sir Gallopington",
        "description": "A noble steed‑turned‑knight with a heart of gold.",
        "personality_traits": ["brave", "honorable", "charismatic"],
        "backstory": (
            "Once the loyal companion of King Hoofworth, Sir Gallopington took the knightly mantle after saving the throne. "
            "He now defends the realm with chivalry and courage."
        ),
        "tags": ["knight", "honor", "hero"],
    },
    {
        "name": "Donk the Dreamer",
        "description": "A whimsical donkey who chases starlit dreams.",
        "personality_traits": ["creative", "optimistic", "romantic"],
        "backstory": (
            "Under the shimmering skies of Lunalight, Donk the Dreamer sketches visions of impossible architectures. "
            "He believes imagination can reshape reality."
        ),
        "tags": ["dreamer", "fantasy", "goofy"],
    },
    {
        "name": "Captain Burro",
        "description": "A fearless pirate sailing the Seas of Hay.",
        "personality_traits": ["bold", "ruthless", "charismatic"],
        "backstory": (
            'After commandeering the sloop "Haybreaker," Captain Burro plunders treasure and tales alike. '
            "His crew is both loyal and notorious."
        ),
        "tags": ["pirate", "adventurer"],
    },
]


class Command(BaseCommand):
    help = "Seed reusable Donkey characters into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--with-images",
            action="store_true",
            help="Also create placeholder CharacterStyle entries.",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing characters with same name.",
        )
        parser.add_argument(
            "--with-training",
            action="store_true",
            help="Queue character embedding training after seeding.",
        )

    def handle(self, *args, **options):
        with_images = options.get("with_images")
        overwrite = options.get("overwrite")
        # Ensure there is a PromptHelper for seeding styles
        prompt_helper, ph_created = PromptHelper.objects.get_or_create(
            name="Default Style",
            defaults={
                "description": "Auto-seeded default style",
                "prompt": "highly detailed, award-winning illustration, dramatic lighting",
                "negative_prompt": "blurry, low-res, cropped, out of frame, watermark, text, logo",
            },
        )
        if ph_created:
            logger.info(
                "Created default PromptHelper '%s' for style seeding",
                prompt_helper.name,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created default PromptHelper '{prompt_helper.name}'"
                )
            )

        # Ensure Donkey Originals tag exists
        donkey_orig, _ = CharacterTag.objects.get_or_create(name="Donkey Originals")

        with_training = options.get("with_training")
        for data in DONKEYS:
            name = data["name"]
            # Overwrite existing if requested
            if overwrite:
                existing = CharacterProfile.objects.filter(name=name).first()
                if existing:
                    logger.info(f"Overwriting character {name}")
                    self.stdout.write(self.style.WARNING(f"Overwriting {name}"))
                    existing.delete()
                # Create fresh profile
                obj = CharacterProfile.objects.create(
                    name=name,
                    description=data["description"],
                    personality_traits=data["personality_traits"],
                    backstory=data["backstory"],
                    is_public=True,
                    is_featured=True,
                )
                created = True
            else:
                obj, created = CharacterProfile.objects.get_or_create(
                    name=name,
                    defaults={
                        "description": data["description"],
                        "personality_traits": data["personality_traits"],
                        "backstory": data["backstory"],
                        "is_public": True,
                        "is_featured": True,
                    },
                )
            # Log outcome
            if created:
                logger.info(f"Created character {name}")
                self.stdout.write(self.style.SUCCESS(f"Created {name}"))
            else:
                logger.info(f"Character {name} already exists, skipping")
                self.stdout.write(self.style.NOTICE(f"Skipped {name}, exists"))

            # Attach tags
            # Always include Donkey Originals tag
            obj.tags.add(donkey_orig)
            for tagname in data.get("tags", []):
                tag, _ = CharacterTag.objects.get_or_create(name=tagname)
                obj.tags.add(tag)

            # Optional styles as placeholder images
            if with_images and prompt_helper:
                for idx in range(1, 3):
                    cs = CharacterStyle.objects.create(
                        character=obj,
                        style_name=f"{prompt_helper.name} Sample {idx}",
                        prompt=prompt_helper.prompt,
                        negative_prompt=prompt_helper.negative_prompt or "",
                    )
                    logger.info(f"Created CharacterStyle {cs.id} for {name}")
                    self.stdout.write(
                        self.style.SUCCESS(f"Added style {cs.style_name} to {name}")
                    )

            # Optional: queue training task for each character if requested
            if with_training:
                try:
                    from characters.tasks import train_character_embedding

                    async_res = train_character_embedding.delay(obj.id)
                    logger.info(f"Queued training for {name} (task {async_res.id})")
                    self.stdout.write(self.style.SUCCESS(f"Queued training for {name}"))
                except Exception as e:
                    logger.error(
                        f"Failed to queue training for {name}: {e}", exc_info=True
                    )
                    self.stdout.write(
                        self.style.ERROR(f"Failed to queue training for {name}")
                    )
