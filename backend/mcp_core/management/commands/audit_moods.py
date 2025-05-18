from django.core.management.base import BaseCommand
from mcp_core.models import ReflectionLog


class Command(BaseCommand):
    help = "Audit and list all unique moods across Reflection Logs."

    def handle(self, *args, **options):
        moods = ReflectionLog.objects.values_list("mood", flat=True)
        unique_moods = sorted(
            set(mood.lower() if mood else "unknown" for mood in moods)
        )

        self.stdout.write(self.style.SUCCESS("🧠 Unique moods detected:"))
        for mood in unique_moods:
            self.stdout.write(f" - {mood}")

        self.stdout.write(
            self.style.SUCCESS(f"✅ Total unique moods: {len(unique_moods)}")
        )
