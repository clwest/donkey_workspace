from django.core.management.base import BaseCommand
import logging
from django.test import Client

# from django.utils import timezone
# from django.utils.text import slugify

# from assistants.models import Assistant, Badge
# from prompts.models import Prompt


class Command(BaseCommand):
    help = "Seed demo assistants with simple prompts and badges"
    logger = logging.getLogger(__name__)

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Recreate demo assistants even if they already exist",
        )
        parser.add_argument(
            "--skip-preview",
            action="store_true",
            help="Skip preview endpoint check",
        )
        parser.add_argument(
            "--skip-badges",
            action="store_true",
            help="Skip badge endpoint check",
        )

    def handle(self, *args, **options):
        from django.utils.text import slugify
        from assistants.models import Assistant, Badge
        from prompts.models import Prompt

        force = options.get("force", False)
        verbosity = options.get("verbosity", 1)
        skip_preview = options.get("skip_preview", False)
        skip_badges = options.get("skip_badges", False)

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
        existing_slugs = list(
            Assistant.objects.filter(is_demo=True).values_list("slug", flat=True)
        )
        if verbosity >= 2:
            self.stdout.write(f"Existing demo slugs: {existing_slugs}")

        for demo in demos:
            slug = slugify(demo["name"])
            if verbosity >= 2:
                self.stdout.write(f"-- Processing {demo['name']} ({slug})")

            assistant = Assistant.objects.filter(name=demo["name"], is_demo=True).first()
            if not assistant:
                assistant = Assistant.objects.filter(slug=slug, is_demo=True).first()

            if assistant and not force:
                # Ensure existing demo assistants have required fields
                patched = False
                if not assistant.system_prompt:
                    prompt, _ = Prompt.objects.get_or_create(
                        title=f"{demo['name']} Seed Prompt",
                        defaults={
                            "content": demo.get("prompt")
                            or "You are a helpful assistant specializing in reflection.",
                            "type": "system",
                            "source": "seed_demo_assistants",
                        },
                    )
                    assistant.system_prompt = prompt
                    patched = True
                if not assistant.memory_context:
                    from mcp_core.models import MemoryContext

                    context = MemoryContext.objects.create(
                        content=f"{assistant.slug}-context"
                    )
                    assistant.memory_context = context
                    patched = True
                if patched:
                    assistant.save()
                    if verbosity >= 2:
                        self.stdout.write(
                            f"🔧 Patched existing demo {assistant.slug}"
                        )
                if verbosity >= 2:
                    self.stdout.write(
                        f"❌ Skipping {demo['name']} (already exists)"
                    )
                continue

            if not assistant and Assistant.objects.filter(slug=slug, is_demo=True).exists() and not force:
                if verbosity >= 2:
                    self.stdout.write(
                        f"❌ Skipping {demo['name']} (slug {slug} already exists)"
                    )
                continue

            if assistant and force:
                assistant.delete()
                if verbosity >= 2:
                    self.stdout.write(f"🔁 Recreating {demo['name']}")

            prompt, _ = Prompt.objects.get_or_create(
                title=f"{demo['name']} Seed Prompt",
                defaults={
                    "content": demo.get("prompt")
                    or "You are a helpful assistant specializing in reflection.",
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
            if not assistant.memory_context:
                from mcp_core.models import MemoryContext

                context = MemoryContext.objects.create(
                    content=f"{assistant.slug}-context"
                )
                assistant.memory_context = context
            if not assistant.system_prompt:
                assistant.system_prompt = prompt
            assistant.save()
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

            # Verify preview and badge routes
            client = Client()
            if not skip_preview:
                try:
                    resp = client.get(f"/api/assistants/{assistant.slug}/preview/")
                    if resp.status_code != 200:
                        self.logger.warning(
                            "Preview route failed for %s: %s",
                            assistant.slug,
                            resp.status_code,
                        )
                except Exception as exc:
                    self.logger.warning(
                        "Preview route error for %s: %s", assistant.slug, exc
                    )
            if not skip_badges:
                try:
                    resp = client.get(f"/api/badges/?assistant={assistant.slug}")
                    if resp.status_code != 200:
                        self.logger.warning(
                            "Badge route failed for %s: %s",
                            assistant.slug,
                            resp.status_code,
                        )
                except Exception as exc:
                    self.logger.warning(
                        "Badge route error for %s: %s", assistant.slug, exc
                    )

        if created_count == 0:
            self.stdout.write("⚠️ No demo assistants were created.")
        else:
            self.stdout.write(
                self.style.SUCCESS(f"\n🌱 Seeded {created_count} demo assistants.")
            )
