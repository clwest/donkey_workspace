from django.core.management.base import BaseCommand
from django.utils.text import slugify
from assistants.models import Assistant

class Command(BaseCommand):
    help = "Seed starter assistants for onboarding demos"

    def handle(self, *args, **options):
        starters = [
            {"name": "Starter Sage", "specialty": "starter", "avatar_style": "robot"},
            {"name": "Demo Guide", "specialty": "guide", "avatar_style": "orb"},
        ]
        created = 0
        for data in starters:
            obj, made = Assistant.objects.get_or_create(
                name=data["name"],
                defaults={
                    "slug": slugify(data["name"]),
                    "specialty": data["specialty"],
                    "avatar_style": data["avatar_style"],
                    "is_demo": True,
                    "is_active": True,
                },
            )
            if made:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} starter assistants"))
