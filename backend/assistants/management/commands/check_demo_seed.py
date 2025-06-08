from django.core.management.base import BaseCommand
from assistants.models import Assistant

EXPECTED = ["prompt-pal", "reflection-sage", "memory-weaver"]

class Command(BaseCommand):
    help = "Verify that demo assistants are seeded"

    def handle(self, *args, **options):
        existing = {
            a.demo_slug: a for a in Assistant.objects.filter(is_demo=True)
        }
        missing = [slug for slug in EXPECTED if slug not in existing]
        for slug in EXPECTED:
            if slug in existing:
                self.stdout.write(self.style.SUCCESS(f"✔ {slug}"))
            else:
                self.stdout.write(self.style.ERROR(f"✖ {slug} missing"))
        if missing:
            self.stdout.write(
                self.style.WARNING(
                    "Run `manage.py seed_demo_assistants` to seed missing demos."
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS("All demo assistants present"))
