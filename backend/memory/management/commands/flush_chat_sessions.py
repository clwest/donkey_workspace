from django.core.management.base import BaseCommand
from assistants.models import Assistant
from assistants.utils.assistant_session import load_session_messages, flush_chat_session
from memory.models import MemoryEntry
from django.utils.timezone import now


class Command(BaseCommand):
    help = "Flush all Redis chat sessions into MemoryEntry records"

    def handle(self, *args, **kwargs):
        flushed = 0
        for assistant in Assistant.objects.all():
            session_id = f"assistant:{assistant.slug}"
            messages = load_session_messages(session_id)

            if not messages:
                self.stdout.write(
                    self.style.WARNING(f"No messages found for {session_id}")
                )
                continue

            for msg in messages:
                if msg["role"] == "user":
                    MemoryEntry.objects.create(
                        event=msg["content"],
                        timestamp=msg.get("timestamp", now()),
                        emotion="neutral",
                        importance=3,
                        is_conversation=True,  # or False if you want reflection-ready items
                    )
                    flushed += 1

            flush_chat_session(session_id)
            self.stdout.write(
                self.style.SUCCESS(f"Flushed session for {assistant.name}")
            )

        self.stdout.write(
            self.style.SUCCESS(f"✅ Flushed {flushed} memory entries total.")
        )
