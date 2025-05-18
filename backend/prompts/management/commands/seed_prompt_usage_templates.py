from django.core.management.base import BaseCommand
from prompts.models import Prompt, PromptUsageTemplate
from assistants.models import Assistant
from django.utils.text import slugify
import random


class Command(BaseCommand):
    help = "Seed the database with Prompt Usage Templates"

    def handle(self, *args, **kwargs):
        prompts = list(Prompt.objects.all())
        assistants = list(Assistant.objects.all())

        if not prompts or not assistants:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Need both prompts and assistants to seed templates."
                )
            )
            return

        triggers = ["on_start", "on_message", "on_reflection", "on_task", "custom"]

        created = 0
        for _ in range(20):
            prompt = random.choice(prompts)
            agent = random.choice(assistants)

            template, created_flag = PromptUsageTemplate.objects.get_or_create(
                prompt=prompt,
                agent=agent,
                trigger_type=random.choice(triggers),
                defaults={
                    "title": f"{prompt.title} for {agent.name}",
                    "description": f"Auto-linked usage of {prompt.title} with {agent.name}.",
                    "is_active": True,
                    "priority": random.randint(1, 5),
                    "fallback_text": "Fallback response in case of error or blank output.",
                },
            )
            if created_flag:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ Seeded {created} prompt usage templates!")
        )
