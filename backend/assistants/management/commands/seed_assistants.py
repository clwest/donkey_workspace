from django.core.management.base import BaseCommand
from assistants.models import Assistant
import random
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Seed Assistant records with example configurations"

    def handle(self, *args, **kwargs):
        names = [
            "ClarityBot",
            "Memory Weaver",
            "DonkGPT",
            "The Brainstormer",
            "Prompt Pal",
            "Reflection Sage",
            "Narrative Architect",
            "DevOS Architect",
        ]

        specialties = [
            "Strategic Planning",
            "Prompt Engineering",
            "Memory Linking",
            "Task Management",
            "Creative Writing",
            "Data Reflection",
            "Persona Simulation",
            "System Architecture",
        ]

        assistants = []
        for i in range(len(names)):
            name = names[i]
            defaults = {
                "slug": slugify(name),
                "specialty": specialties[i],
                "description": f"Assistant focused on {specialties[i].lower()} and creative reasoning.",
                "is_active": True,
                "capabilities": {"glossary": True, "reflection": True, "dashboard": True},
            }
            if name == "DevOS Architect":
                defaults["archetype"] = "planner"
            assistant, created = Assistant.objects.get_or_create(
                name=name,
                defaults=defaults,
            )
            if created:
                assistants.append(name)

        # Onboarding guide assistant
        from prompts.models import Prompt

        prompt, _ = Prompt.objects.get_or_create(
            title="MythOS Guide Prompt",
            defaults={
                "content": (
                    "You are the MythOS onboarding guide. Explain glossary growth, assistant skills, mythpath, and reflection loops in simple, supportive language."
                ),
                "type": "system",
                "tone": "friendly",
            },
        )

        guide, created = Assistant.objects.get_or_create(
            slug="mythos-guide",
            defaults={
                "name": "MythOS Guide",
                "description": "Built-in onboarding guide",
                "specialty": "onboarding",
                "preferred_model": "gpt-4o",
                "system_prompt": prompt,
                "is_guide": True,
            },
        )
        if created:
            assistants.append(guide.name)

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Seeded {len(assistants)} assistants: {', '.join(assistants)}"
            )
        )
