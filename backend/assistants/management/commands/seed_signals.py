# assistants/management/commands/seed_signals.py

from django.core.management.base import BaseCommand
from assistants.models import SignalSource
from django.utils import timezone
import random

SAMPLE_SOURCES = [
    {
        "platform": "Twitter",
        "name": "Pliny the Liberator",
        "handle": "@pliny",
        "url": "https://twitter.com/pliny",
        "priority": 1,
    },
    {
        "platform": "YouTube",
        "name": "AI News Daily",
        "handle": None,
        "url": "https://youtube.com/ainews",
        "priority": 2,
    },
    {
        "platform": "Blog",
        "name": "OpenAI Research Updates",
        "handle": None,
        "url": "https://openai.com/research",
        "priority": 1,
    },
    {
        "platform": "Newsletter",
        "name": "Anthropic Announcements",
        "handle": None,
        "url": "https://anthropic.com/news",
        "priority": 2,
    },
]


class Command(BaseCommand):
    help = "Seeds some Signal Sources for agents to monitor."

    def handle(self, *args, **kwargs):
        count = 0
        for source in SAMPLE_SOURCES:
            obj, created = SignalSource.objects.get_or_create(
                platform=source["platform"],
                name=source["name"],
                defaults={
                    "handle": source["handle"],
                    "url": source["url"],
                    "priority": source["priority"],
                    "active": True,
                    "created_at": timezone.now(),
                },
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f"📡 Seeded {count} signal sources!"))
