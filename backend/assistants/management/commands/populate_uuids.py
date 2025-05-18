from django.core.management.base import BaseCommand
from assistants.models import AssistantChatMessage
import uuid
import random

FEEDBACK_CHOICES = [
    "helpful",
    "not_helpful",
    "too_long",
    "too_short",
    "irrelevant",
    "unclear",
    "perfect",
]

TOPIC_SEEDS = [
    "Productivity",
    "Startup Planning",
    "Marketing Ideas",
    "Tech Support",
    "Prompt Engineering",
    "Philosophy Chat",
]


class Command(BaseCommand):
    help = (
        "Populate missing UUIDs, topics, and feedback for AssistantChatMessage objects."
    )

    def handle(self, *args, **options):
        updated_count = 0

        messages = AssistantChatMessage.objects.all()
        for msg in messages:
            changed = False

            if not msg.uuid:
                msg.uuid = uuid.uuid4()
                changed = True

            if not msg.topic:
                msg.topic = random.choice(TOPIC_SEEDS)
                changed = True

            if not msg.feedback:
                msg.feedback = random.choice(FEEDBACK_CHOICES)
                changed = True

            if changed:
                msg.save()
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Populated fields on {updated_count} AssistantChatMessages"
            )
        )
