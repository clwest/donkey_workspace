"""Bootstrap a DevOps assistant and project with dev docs.

This management command is a quick start for linking a new assistant to a
project and seeding it with documentation. It performs the following steps:

1. Create (or fetch) a DevOps-focused ``Assistant`` instance.
2. Create a ``Project`` tied to that assistant.
3. Attach all ``DevDoc`` records to the project for context.
4. Create an ``AssistantProject`` record to log the relationship.
5. Seed an ``AssistantThoughtLog`` entry summarizing the docs reviewed.
"""

from django.core.management.base import BaseCommand
from assistants.models import Assistant, AssistantProject, AssistantThoughtLog
from mcp_core.models import DevDoc
from project.models import Project  # ← main Project model
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Command(BaseCommand):
    help = "Seed a DevOps Assistant, Project, and attach DevDocs as thought context."

    def handle(self, *args, **options):
        assistant_name = "Zeno the Build Wizard"
        project_name = "DevOps Reflection"

        # Get fallback user if needed
        fallback_user = get_user_model().objects.first()

        # Get or create assistant
        assistant, created = Assistant.objects.get_or_create(
            slug=slugify(assistant_name),
            defaults={
                "name": assistant_name,
                "description": "A wizard-like assistant focused on understanding the system through documentation and reflection.",
                "specialty": "DevOps, system wiring, prompt logic",
                "preferred_model": "gpt-4o",
            },
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"{'🧙 Created' if created else '♻️ Found'} assistant: {assistant.name}"
            )
        )

        project_slug = slugify(project_name)

        # Create or get the main project
        project, created = Project.objects.get_or_create(
            slug=project_slug,
            defaults={
                "title": project_name,
                "description": "A project to analyze and reflect on Donkey AI's documentation.",
                "user": assistant.created_by or fallback_user,
                "project_type": "assistant",
                "assistant": assistant,  # link assistant → project
            },
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"{'📁 Created' if created else '📂 Found'} project: {project.title}"
            )
        )

        # Pull dev docs and assign
        docs = DevDoc.objects.all()
        project.dev_docs.set(docs)  # attach docs → project

        # Create AssistantProject linking assistant ↔ project
        assistant_project, _ = AssistantProject.objects.get_or_create(
            title=project.title,
            assistant=assistant,
            defaults={
                "description": project.description,
                "created_by": assistant.created_by or fallback_user,
            },
        )

        # Log summary
        doc_titles = [doc.title for doc in docs]
        summary = (
            f"I've been assigned to audit and reflect on {len(docs)} documentation files. "
            "Here are the titles I've reviewed:\n\n"
            + "\n".join(f"- {title}" for title in doc_titles)
        )

        AssistantThoughtLog.objects.create(
            assistant=assistant,
            project=project,
            thought_type="initial_observation",
            thought=summary,
        )

        self.stdout.write(
            self.style.SUCCESS(f"🧠 Logged initial reflection with {len(docs)} docs.")
        )
        self.stdout.write(
            self.style.SUCCESS("✅ DevOps assistant and project setup complete!")
        )
