from django.core.management.base import BaseCommand
from django.utils import timezone
from assistants.models import Assistant, TokenUsage
from project.models import Project
from memory.models import MemoryEntry
from uuid import uuid4
from datetime import timedelta
import random


class Command(BaseCommand):
    help = "Seed example chat sessions with linked memory and token usage"

    def handle(self, *args, **kwargs):
        assistants = Assistant.objects.all()
        if not assistants.exists():
            self.stdout.write(
                self.style.ERROR("❌ No assistants found. Seed assistants first.")
            )
            return

        for assistant in assistants:
            session_id = uuid4()
            created_at = timezone.now() - timedelta(days=random.randint(1, 30))

            # Create ChatSession
            project = Project.objects.filter(assistant=assistant).first()
            thread = None
            if project:
                thread = project.thread or project.narrative_thread

            session = assistant.chatsession_set.create(
                session_id=session_id,
                assistant=assistant,
                project=project,
                narrative_thread=thread,
                thread=thread,
                created_at=created_at,
                updated_at=created_at,
                last_active=created_at,
            )
            if project:
                session.save()

            # Create a few memory entries
            for i in range(random.randint(2, 4)):
                event = f"Simulated memory event {i+1} for {assistant.name}"
                MemoryEntry.objects.create(
                    event=event,
                    emotion=random.choice(["happy", "curious", "neutral"]),
                    importance=random.randint(1, 5),
                    chat_session=session,
                )

            # Seed token usage
            TokenUsage.objects.create(
                session=session,
                assistant=assistant,
                project=project,
                prompt_tokens=random.randint(50, 150),
                completion_tokens=random.randint(100, 300),
                total_tokens=0,
                total_cost=round(random.uniform(0.01, 0.10), 3),
                usage_type="chat",
            )

            self.stdout.write(
                self.style.SUCCESS(f"✅ Seeded chat session for {assistant.name}")
            )
