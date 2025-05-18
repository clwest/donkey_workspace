from django.core.management.base import BaseCommand
from images.models import ThemeHelper


class Command(BaseCommand):
    help = "Seeds default built-in themes into ThemeHelper"

    def handle(self, *args, **options):
        themes = [
            {
                "name": "Snowy Mountains",
                "description": "A magical winter landscape filled with icy peaks and swirling snow.",
                "prompt": "snow-covered mountains, cold mist, frozen trees, hushed silence, twilight glow",
                "negative_prompt": "summer, sunshine, beach, desert, tropical, modern elements",
                "category": "Scenic",
                "tags": ["snow", "mountains", "winter", "ice", "cold"],
            },
            {
                "name": "Fantasy Kingdom",
                "description": "Lush forests and towering castles brimming with enchantment.",
                "prompt": "medieval fantasy kingdom, enchanted forest, majestic castle, magical aura, lush greenery",
                "negative_prompt": "technology, cars, neon lights, modern clothing",
                "category": "Fantasy",
                "tags": ["fantasy", "kingdom", "castle", "magic", "forest"],
            },
            {
                "name": "Cyberpunk City",
                "description": "Rain-soaked alleys and glowing neon skyscrapers in a high-tech world.",
                "prompt": "cyberpunk cityscape, neon lights, rainy night, futuristic tech, digital signage",
                "negative_prompt": "nature, medieval elements, rustic design, greenery",
                "category": "Sci-Fi",
                "tags": ["cyberpunk", "neon", "city", "tech", "future"],
            },
            {
                "name": "Enchanted Forest",
                "description": "A mysterious woodland aglow with bioluminescent magic.",
                "prompt": "bioluminescent trees, glowing mushrooms, fairy lights, magical mist",
                "negative_prompt": "urban environment, pollution, concrete",
                "category": "Fantasy",
                "tags": ["forest", "enchanted", "magic", "glow", "fairy"],
            },
            {
                "name": "Outer Space",
                "description": "Alien worlds, distant galaxies, and the great unknown.",
                "prompt": "nebula background, alien planets, spaceship, cosmic dust, stars",
                "negative_prompt": "Earth elements, ground-based visuals, nature",
                "category": "Sci-Fi",
                "tags": ["space", "stars", "alien", "cosmos", "galaxy"],
            },
        ]

        for theme in themes:
            obj, created = ThemeHelper.objects.get_or_create(
                name=theme["name"],
                defaults={
                    "description": theme["description"],
                    "prompt": theme["prompt"],
                    "negative_prompt": theme["negative_prompt"],
                    "category": theme["category"],
                    "tags": theme["tags"],
                    "is_builtin": True,
                    "is_public": True,
                    "is_featured": True,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added theme: {obj.name}"))
            else:
                self.stdout.write(f"Skipped existing theme: {obj.name}")
