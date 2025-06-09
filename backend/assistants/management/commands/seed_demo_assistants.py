from django.core.management.base import BaseCommand

# from django.utils import timezone
# from django.utils.text import slugify

# from assistants.models import Assistant, Badge
# from prompts.models import Prompt


class Command(BaseCommand):
    help = "Seed demo assistants with simple prompts and badges"

    def handle(self, *args, **options):
        from django.utils.text import slugify
        from assistants.models import Assistant, Badge
        from prompts.models import Prompt

        force = options.get("force", False)
        verbosity = options.get("verbosity", 1)

        demos = [
            {
                "name": "Reflection Sage",
                "specialty": "reflection",
                "avatar": "https://example.com/sage.png",
                "prompt": "You help users reflect on their ideas in a concise way.",
                "badges": ["reflection_ready"],
                "intro": "Ask me to review your latest thought.",
            },
            {
                "name": "Prompt Pal",
                "specialty": "prompt_design",
                "avatar": "https://example.com/prompt-pal.png",
                "prompt": "You help users craft clear and creative prompts for AI systems.",
                "badges": ["prompt_helper"],
                "intro": "Let’s shape your next prompt together.",
            },
            {
                "name": "Memory Weaver",
                "specialty": "memory_management",
                "avatar": "https://example.com/memory-weaver.png",
                "prompt": "You help users organize and connect insights over time.",
                "badges": ["memory_archivist"],
                "intro": "Ask me to thread memories into useful insights.",
            },
        ]

        created_count = 0

        for demo in demos:
            slug = slugify(demo["name"])
            assistant = Assistant.objects.filter(
                name=demo["name"], is_demo=True
            ).first()

            if assistant and not force:
                if verbosity >= 2:
                    self.stdout.write(f"❌ Skipping {demo['name']} (already exists)")
                continue

            if assistant and force:
                assistant.delete()
                if verbosity >= 2:
                    self.stdout.write(f"🔁 Recreating {demo['name']}")

            prompt, _ = Prompt.objects.get_or_create(
                title=f"{demo['name']} Seed Prompt",
                defaults={
                    "content": demo["prompt"],
                    "type": "system",
                    "source": "seed_demo_assistants",
                },
            )

            assistant = Assistant.objects.create(
                name=demo["name"],
                demo_slug=slug,
                specialty=demo["specialty"],
                avatar=demo["avatar"],
                system_prompt=prompt,
                prompt_title=prompt.title,
                intro_text=demo["intro"],
                is_demo=True,
                is_active=True,
            )
            created_count += 1

            # Add badges if they exist
            for badge_slug in demo.get("badges", []):
                badge = Badge.objects.filter(slug=badge_slug).first()
                if badge:
                    current = set(assistant.skill_badges or [])
                    current.add(badge.slug)
                    assistant.skill_badges = sorted(current)
                    assistant.save(update_fields=["skill_badges"])

            if verbosity >= 1:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Created demo: {demo['name']}")
                )

        if created_count == 0:
            self.stdout.write("⚠️ No demo assistants were created.")
        else:
            self.stdout.write(
                self.style.SUCCESS(f"\n🌱 Seeded {created_count} demo assistants.")
            )
