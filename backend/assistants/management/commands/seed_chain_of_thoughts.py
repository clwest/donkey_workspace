from django.core.management.base import BaseCommand
from assistants.models import Assistant, AssistantThoughtLog
from django.utils import timezone

EXAMPLES = [
    {
        "thought": "The user asked whether donkeys can swim. I need to consider animal physiology and prior knowledge to respond.",
        "thought_trace": (
            "🧩 Chain of Thought:\n"
            "- Donkeys are mammals and most mammals can swim instinctively.\n"
            "- However, swimming ability may vary depending on breed and environment.\n"
            "- Safety and supervision are key when introducing donkeys to water.\n"
            "- The user may be asking out of curiosity or planning to expose a donkey to water.\n"
            "➡️ Final answer: Yes, most donkeys can swim, but it should be done safely and with care."
        ),
        "thought_type": "cot",
        "role": "assistant",
    },
    {
        "thought": "The user is struggling with creative burnout. I should explore emotional cues and suggest small, achievable tasks.",
        "thought_trace": (
            "🧩 Chain of Thought:\n"
            "- User mentioned feeling unmotivated and overwhelmed.\n"
            "- This suggests cognitive fatigue and emotional overload.\n"
            "- Recommending tiny wins and dopamine-boosting actions could help.\n"
            "- Maybe frame it as a creative recharge, not productivity.\n"
            "➡️ Final answer: Try something fun and low-pressure today. You don’t need to be productive—just feel a spark again."
        ),
        "thought_type": "cot",
        "role": "assistant",
    },
]


class Command(BaseCommand):
    help = "Seed chain-of-thought examples for DonkGPT"

    def handle(self, *args, **kwargs):
        try:
            assistant = Assistant.objects.get(slug="donkgpt")
        except Assistant.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ DonkGPT assistant not found."))
            return

        for entry in EXAMPLES:
            thought = AssistantThoughtLog.objects.create(
                assistant=assistant,
                thought=entry["thought"],
                thought_trace=entry["thought_trace"],
                thought_type=entry["thought_type"],
                role=entry["role"],
                created_at=timezone.now(),
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Seeded: {thought.thought[:60]}"))

        self.stdout.write(
            self.style.SUCCESS("🌱 Done seeding chain-of-thought entries!")
        )
