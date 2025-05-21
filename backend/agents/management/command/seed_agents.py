from django.core.management.base import BaseCommand
from agents.models import Agent
from assistants.models import Assistant
from django.utils.text import slugify

class Command(BaseCommand):
    help = "Seeds initial agents and assigns sub-assistants to a parent"

    def handle(self, *args, **kwargs):
        assignments = [
            {
                "parent_slug": "zeno-the-build-wizard",
                "agent": {
                    "name": "LangChain Agent",
                    "description": "Handles all LangChain-related tasks and reasoning flows.",
                    "preferred_llm": "gpt-4o",
                    "execution_mode": "sequential",
                },
                "assistant_name_prefix": "LangChain Assistant",
            },
            {
                "parent_slug": "zeno-the-build-wizard",
                "agent": {
                    "name": "Stability Agent",
                    "description": "Manages AI image/video generation via Stability tools.",
                    "preferred_llm": "gpt-4o",
                    "execution_mode": "parallel",
                },
                "assistant_name_prefix": "Stability AI Assistant",
            },
            {
                "parent_slug": "zeno-the-build-wizard",
                "agent": {
                    "name": "Solidity Agent",
                    "description": "Helps parse, document, and reflect on Solidity development guides.",
                    "preferred_llm": "gpt-4o",
                    "execution_mode": "sequential",
                },
                "assistant_name_prefix": "Solidity Smart Contract Assistant",
            },
        ]

        for entry in assignments:
            try:
                parent = Assistant.objects.get(slug=entry["parent_slug"])
            except Assistant.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Parent assistant '{entry['parent_slug']}' not found."))
                continue

            # Create agent
            agent_data = entry["agent"]
            agent_slug = slugify(agent_data["name"])
            if not Agent.objects.filter(slug=agent_slug, assistant=parent).exists():
                Agent.objects.create(
                    assistant=parent,
                    name=agent_data["name"],
                    slug=agent_slug,
                    description=agent_data["description"],
                    preferred_llm=agent_data["preferred_llm"],
                    execution_mode=agent_data["execution_mode"],
                )
                self.stdout.write(self.style.SUCCESS(f"✅ Agent '{agent_data['name']}' created."))

            # Assign sub-assistants
            matching_assistants = Assistant.objects.filter(name__icontains=entry["assistant_name_prefix"])
            for sub in matching_assistants:
                if sub == parent:
                    continue
                sub.parent_assistant = parent
                sub.save()
                self.stdout.write(self.style.WARNING(f"🔗 Linked '{sub.name}' to parent '{parent.name}'"))

        self.stdout.write(self.style.SUCCESS("🎯 Agent seeding + sub-assistant assignment complete!"))