from django.core.management.base import BaseCommand
from assistants.helpers.collaboration import detect_conflict_signals


class Command(BaseCommand):
    help = "List recent thoughts with high tension"

    def handle(self, *args, **options):
        thoughts = detect_conflict_signals()
        for t in thoughts:
            self.stdout.write(f"{t.assistant.name}: {t.thought[:50]}")
        self.stdout.write(self.style.SUCCESS("Scan complete"))
