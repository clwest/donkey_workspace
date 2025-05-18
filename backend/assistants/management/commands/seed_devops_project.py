from django.core.management.base import BaseCommand
from assistants.models import Assistant, AssistantProject
from prompts.models import Prompt

class Command(BaseCommand):
    help = "Seed a DevOps assistant and linked project"

    def handle(self, *args, **kwargs):
        # ✅ Create or fetch the system prompt
        system_prompt, _ = Prompt.objects.get_or_create(
            title="DevOps Assistant Prompt",
            defaults={
                "content": (
                    "You are a DevOps assistant who specializes in automation, CI/CD, infrastructure-as-code, "
                    "and deployment troubleshooting. Stay focused, concise, and always explain tradeoffs when recommending tools."
                ),
                "type": "system",
                "tone": "confident",
                "model_backend": "gpt-4o"
            },
        )

        # ✅ Create Assistant
        assistant, _ = Assistant.objects.get_or_create(
            name="Opsie the Infra Owl",
            slug="opsie-the-infra-owl",
            defaults={
                "description": "A wise, calm DevOps assistant who automates the un-automatable.",
                "specialty": "DevOps & Infrastructure",
                "personality": "Wise, helpful, and obsessed with YAML best practices.",
                "tone": "confident",
                "preferred_model": "gpt-4o",
                "system_prompt": system_prompt,
            }
        )

        # ✅ Create Project
        project, _ = AssistantProject.objects.get_or_create(
            title="CI/CD Pipeline Upgrade",
            assistant=assistant,
            defaults={
                "goal": (
                    "Audit and upgrade the current CI/CD pipeline to support multi-environment staging, "
                    "automated rollback, and test coverage reporting for both backend and frontend."
                )
            },
        )

        self.stdout.write(self.style.SUCCESS(f"✅ Assistant: {assistant.name}"))
        self.stdout.write(self.style.SUCCESS(f"📁 Project: {project.title}"))