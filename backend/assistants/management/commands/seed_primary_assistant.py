from django.core.management.base import BaseCommand
from django.utils.text import slugify

from assistants.models import Assistant, AssistantThoughtLog
from assistants.views.bootstrap import prompt_to_assistant

THOUGHTS = [
    {
        "thought": "I must ensure agents are coordinating without redundant efforts.",
        "importance": 5,
        "emotion": "focused",
    },
    {
        "thought": "We have no active objective for memory summarization. That should be resolved.",
        "importance": 4,
        "emotion": "curious",
    },
    {
        "thought": "Prompt experiments are increasing — this might require its own assistant soon.",
        "importance": 4,
        "emotion": "reflective",
    },
]


class Command(BaseCommand):
    help = "Seed the Primary Orchestrator assistant"

    def handle(self, *args, **options):
        slug = slugify("Primary Orchestrator")
        assistant = Assistant.objects.filter(slug=slug).first()
        if not assistant:
            assistant = prompt_to_assistant(
                name="Primary Orchestrator",
                tone="strategic",
                personality="intelligent, calm, curious",
            )
            created = True
        else:
            created = False

        for item in THOUGHTS:
            AssistantThoughtLog.objects.get_or_create(
                assistant=assistant,
                thought=item["thought"],
            )

        if created:
            self.stdout.write(self.style.SUCCESS("✅ Primary assistant created."))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Primary assistant already exists."))
