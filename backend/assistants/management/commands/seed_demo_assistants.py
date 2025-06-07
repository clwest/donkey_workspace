from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from assistants.models import Assistant, Badge
from prompts.models import Prompt


class Command(BaseCommand):
    help = "Seed demo assistants with simple prompts and badges"

    def handle(self, *args, **options):
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
                "specialty": "prompt engineering",
                "avatar": "https://example.com/promptpal.png",
                "prompt": "You assist with crafting effective prompts.",
                "badges": ["glossary_apprentice"],
                "intro": "Need a better prompt? Let's craft one!",
            },
            {
                "name": "Memory Weaver",
                "specialty": "memory",
                "avatar": "https://example.com/weaver.png",
                "prompt": "You connect conversations into coherent memories.",
                "badges": ["vocab_proficient"],
                "intro": "I'll weave your chats into lasting insights.",
            },
        ]

        created = 0
        for data in demos:
            prompt_obj, _ = Prompt.objects.get_or_create(
                title=f"{data['name']} Demo Prompt",
                defaults={
                    "content": data["prompt"],
                    "type": "system",
                    "source": "demo",
                },
            )
            assistant, made = Assistant.objects.get_or_create(
                slug=slugify(data["name"]),
                defaults={
                    "name": data["name"],
                    "specialty": data["specialty"],
                    "description": data["prompt"],
                    "system_prompt": prompt_obj,
                    "avatar": data["avatar"],
                    "skill_badges": data["badges"],
                    "badge_history": [
                        {
                            "timestamp": timezone.now().isoformat(),
                            "badges": data["badges"],
                        }
                    ],
                    "intro_text": data["intro"],
                    "is_demo": True,
                    "demo_slug": slugify(data["name"]),
                },
            )
            if made:
                created += 1
            # ensure badges exist
            for b in data["badges"]:
                Badge.objects.get_or_create(
                    slug=b, defaults={"label": b.title(), "emoji": "🏅"}
                )

            if not assistant.memories.exists():
                from assistants.utils.starter_chat import seed_chat_starter_memory

                seed_chat_starter_memory(assistant)

        self.stdout.write(self.style.SUCCESS(f"Seeded {created} demo assistants"))
