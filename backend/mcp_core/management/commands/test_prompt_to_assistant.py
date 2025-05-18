# mcp_core/management/commands/test_prompt_to_assistant.py

from django.core.management.base import BaseCommand
from prompts.models import Prompt
from assistants.models import Assistant, AssistantProject
from prompts.utils.embeddings import get_prompt_embedding
from embeddings.helpers.helpers_io import save_embedding
import uuid

class Command(BaseCommand):
    help = "🧪 Run an end-to-end test: Prompt ➝ Assistant ➝ Project"

    def handle(self, *args, **kwargs):
        prompt = self.generate_test_prompt()
        assistant = self.create_assistant_from_prompt(prompt)
        project = self.bootstrap_project_from_assistant(assistant)

        self.stdout.write(self.style.SUCCESS(f"✅ Created Assistant: {assistant.name}"))
        self.stdout.write(self.style.SUCCESS(f"📁 Linked Project: {project.title}"))

    def generate_test_prompt(self):
        title = "TEST: Simple Assistant Bootstrap"
        content = (
            "You are a test assistant. Help users perform basic tasks such as creating projects, "
            "generating content, and logging memory. You do not need to be clever or creative. "
            "Just simulate assistant behavior."
        )

        prompt = Prompt.objects.create(
            title=title,
            slug=f"test-{uuid.uuid4().hex[:8]}",
            content=content,
            type="system",
            source="test-suite",
            tone="neutral",
            token_count=len(content.split()),
            is_draft=False,
        )

        fake_embedding = [0.0] * 1536  # skip token usage
        prompt.embedding = fake_embedding
        prompt.save()
        save_embedding(prompt, fake_embedding)

        return prompt

    def create_assistant_from_prompt(self, prompt):
        assistant = Assistant.objects.create(
            name=prompt.title[:40],
            system_prompt=prompt,
            tone="neutral",
            personality="TEST MODE",
            specialty="testing-assistant-pipeline",
            preferred_model="gpt-4o",
            is_demo=True,
        )
        return assistant

    def bootstrap_project_from_assistant(self, assistant):
        project = AssistantProject.objects.create(
            assistant=assistant,
            title=f"Auto Project for {assistant.name}",  # <- updated line
            description="This is a test-generated project based on assistant intent.",
            status="active",
        )
        return project
