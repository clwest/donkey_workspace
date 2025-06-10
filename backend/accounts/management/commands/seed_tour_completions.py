from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import UserTourCompletion

class Command(BaseCommand):
    help = "Seed demo tour completion records"

    def handle(self, *args, **options):
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            username="seed_user", defaults={"email": "seed@example.com"}
        )
        obj, created = UserTourCompletion.objects.get_or_create(user=user)
        if created:
            self.stdout.write(self.style.SUCCESS("✅ Seeded 1 tour completion"))
        else:
            self.stdout.write("Tour completion already exists")
