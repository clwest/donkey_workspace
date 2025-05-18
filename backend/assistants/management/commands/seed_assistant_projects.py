# assistants/management/commands/seed_assistant_projects.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from project.models import Project
import random


class Command(BaseCommand):
    help = "Seed the database with assistant projects."

    def handle(self, *args, **options):
        User = get_user_model()

        # Reuse or create a default seeding user
        user, _ = User.objects.get_or_create(
            username="seed_user",
            defaults={"email": "seed@example.com", "password": "notsecure"},
        )

        titles = [
            "Build Personal Knowledge Base",
            "Launch AI Content Assistant",
            "Optimize Memory Management",
            "Develop Reflection Insights Dashboard",
            "Prototype Autonomous Planning Agent",
            "Create AI-Powered Daily Journal",
            "Launch Task Prioritization Agent",
            "Enhance Memory-Driven Reflection",
            "Optimize Assistant Collaboration Layer",
            "Design Memory Pruning Engine",
        ]

        descriptions = [
            "An initiative focused on creating a structured memory retrieval system for personal data storage.",
            "A project to launch a GPT-powered assistant for drafting, editing, and improving written content.",
            "Improving the way memories are processed, retrieved, and summarized by the assistant system.",
            "Building a dashboard to visualize and extract insights from memory reflection cycles.",
            "Prototype an autonomous agent capable of chaining tasks and adjusting plans in real time.",
            "Develop an AI-powered tool for daily journaling, reflection, and emotional tagging.",
            "An agent that reviews tasks and reorders them dynamically based on shifting priorities.",
            "Enhance how assistants use historical memory to reflect and adapt over time.",
            "Create a collaboration system where multiple agents work together on linked tasks.",
            "Design a pruning algorithm to automatically archive or forget low-importance memories.",
        ]

        created = 0

        for title, description in zip(titles, descriptions):
            Project.objects.create(
                user=user,  # 👈 REQUIRED
                title=title,
                description=description,
                status=random.choice(["active", "completed", "archived"]),
            )
            created += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ Seeded {created} assistant projects successfully!")
        )
