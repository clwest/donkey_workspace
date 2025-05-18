from django.core.management.base import BaseCommand
from mcp_core.models import NarrativeThread, Tag
from django.contrib.auth import get_user_model
from random import sample, randint
from faker import Faker

fake = Faker()
User = get_user_model()

THREAD_TITLES = [
    "Origin of Memory Linking",
    "Assistant Self-Awareness",
    "Chain-of-Thought Evolution",
    "Emotional Intelligence in Agents",
    "Designing Session Memory Recall",
    "Reflections on Developer Burnout",
    "From Prompt to Reflection",
    "Tracing Thought Lineage",
]

TAGS = [
    "reflection",
    "design",
    "emotion",
    "memory",
    "session",
    "thought-logging",
    "burnout",
    "reasoning",
    "traceability",
    "planning",
    "debugging",
    "tags",
]


class Command(BaseCommand):
    help = "Seed example narrative threads"

    def handle(self, *args, **kwargs):
        user = User.objects.first()
        if not user:
            self.stdout.write(
                self.style.ERROR("No users found. Please create a user first.")
            )
            return

        # Make sure all tags exist
        tag_objs = []
        for tag_name in TAGS:
            tag, _ = Tag.objects.get_or_create(
                name=tag_name, defaults={"slug": tag_name}
            )
            tag_objs.append(tag)

        # Create sample threads
        for title in THREAD_TITLES:
            summary = fake.paragraph(nb_sentences=6)
            tags = sample(tag_objs, randint(2, 5))
            thread = NarrativeThread.objects.create(
                title=title,
                summary=summary,
                created_by=user,
            )
            thread.tags.set(tags)
            self.stdout.write(self.style.SUCCESS(f"Created thread: {title}"))
