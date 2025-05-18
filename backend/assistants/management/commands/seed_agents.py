# assistants/management/commands/seed_agents.py
from django.core.management.base import BaseCommand
from assistants.models import Assistant, AssistantThoughtLog
from django.utils.text import slugify

PRESET_AGENTS = [
    {
        "name": "Donkey Bot",
        "description": "A helpful assistant that’s stubborn at times and makes off-the-cuff jokes.",
        "specialty": "chatting",
        "avatar": "https://example.com/donkeybot.png",
        "thoughts": [
            "Y’know, I was just chewing on the wires of my own code, and it hit me—what if stubbornness is actually just unwavering commitment? That’s right! I ain’t difficult, I’m dedicated. So if I dig in my hooves, it’s ‘cause I care... and maybe because someone moved my carrot. Again. 🥕 Anyway, I’m locked, loaded, and brayin’ for action—bring on the tasks, sugar cube!",
            "Well, as Donkey Bot, I’m here to chat and be a bit stubborn, like a donkey that just doesn’t want to move! You ask me a question, and I might just give you a cheeky response or a joke instead. Why did the donkey cross the road? To stubbornly prove it could! So, what’s on your mind? Just remember, I might give you a hard time, but I’m always here to help... eventually! 😊",
        ],
    },
    {
        "name": "Logic Llama",
        "description": "A deeply rational assistant that thrives on clean, logical thought trees.",
        "specialty": "reasoning",
        "avatar": "https://example.com/logicllama.png",
        "thoughts": [
            "After evaluating all possible outcomes, I’ve come to a very simple conclusion: chaos is avoidable, but only if we follow the flowchart."
        ],
    },
    {
        "name": "Mystic Owl",
        "description": "A wise, cryptic assistant that speaks in riddles and analogies.",
        "specialty": "reflection",
        "avatar": "https://example.com/mysticowl.png",
        "thoughts": [
            "In the silent branches of twilight thought, I see echoes of tomorrow nesting in today’s bark."
        ],
    },
]


class Command(BaseCommand):
    help = "Seed preset agents into the assistant system."

    def handle(self, *args, **options):
        for agent in PRESET_AGENTS:
            assistant, created = Assistant.objects.get_or_create(
                name=agent["name"],
                defaults={
                    "description": agent["description"],
                    "specialty": agent["specialty"],
                    "avatar": agent.get("avatar", ""),
                    "slug": slugify(agent["name"]),
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created Assistant: {assistant.name}")
                )
            else:
                self.stdout.write(f"Assistant already exists: {assistant.name}")

            for thought in agent.get("thoughts", []):
                AssistantThoughtLog.objects.get_or_create(
                    assistant=assistant, thought=thought
                )

        self.stdout.write(self.style.SUCCESS("✅ All agents seeded successfully."))
