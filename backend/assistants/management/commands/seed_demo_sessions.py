from django.core.management.base import BaseCommand
from assistants.models import Assistant
from assistants.models.demo_usage import DemoSessionLog
from django.utils import timezone
import uuid
import random

class Command(BaseCommand):
    help = "Seed demo session logs for demo assistants"

    def handle(self, *args, **options):
        count = 0
        for assistant in Assistant.objects.filter(is_demo=True):
            for i in range(3):
                DemoSessionLog.objects.create(
                    assistant=assistant,
                    session_id=uuid.uuid4().hex,
                    started_at=timezone.now(),
                    ended_at=timezone.now(),
                    message_count=random.randint(1, 5),
                    starter_query=f"Example query {i+1}",
                )
                count += 1
        self.stdout.write(self.style.SUCCESS(f"✅ Seeded {count} demo sessions"))
