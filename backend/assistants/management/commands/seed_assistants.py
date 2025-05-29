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
        ]

        specialties = [
            "Strategic Planning",
            "Prompt Engineering",
            "Memory Linking",
            "Task Management",
            "Creative Writing",
            "Data Reflection",
            "Persona Simulation",
        ]

        assistants = []
        for i in range(len(names)):
            name = names[i]
            assistant, created = Assistant.objects.get_or_create(
                name=name,
                defaults={
                    "slug": slugify(name),
                    "specialty": specialties[i],
                    "description": f"Assistant focused on {specialties[i].lower()} and creative reasoning.",
                    "is_active": True,
                    "capabilities": {"glossary": True, "reflection": True, "dashboard": True},
                },
            )
            if created:
                assistants.append(name)

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Seeded {len(assistants)} assistants: {', '.join(assistants)}"
            )
        )
