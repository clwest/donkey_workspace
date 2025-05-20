from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from assistants.models import Assistant, CouncilSession


class Command(BaseCommand):
    help = "Seed a demo council session with a few assistants"

    def handle(self, *args, **options):
        user = get_user_model().objects.first()
        members = list(Assistant.objects.filter(is_active=True)[:3])
        session = CouncilSession.objects.create(topic="Demo Council", created_by=user)
        session.members.set(members)
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Created council session {session.id} with {len(members)} members"
            )
        )
