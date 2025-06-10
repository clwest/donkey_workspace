from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from feedback.models import FeedbackEntry


class Command(BaseCommand):
    help = "Seed sample feedback entries"

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.first()
        FeedbackEntry.objects.get_or_create(
            assistant_slug="demo", category="bug", description="Overlay error", user=user
        )
        FeedbackEntry.objects.get_or_create(
            assistant_slug="demo", category="idea", description="Add loading spinner", user=user
        )
        FeedbackEntry.objects.get_or_create(
            assistant_slug="demo", category="bug", description="Tour button misaligned", user=user
        )
        self.stdout.write(self.style.SUCCESS("Seeded feedback"))
