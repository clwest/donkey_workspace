from django.core.management.base import BaseCommand
from memory.models import GlossaryChangeEvent

class Command(BaseCommand):
    """List glossary anchor suggestions (boost=0)."""

    help = "Show glossary anchor suggestions recorded via API"

    def handle(self, *args, **options):
        suggestions = GlossaryChangeEvent.objects.filter(boost=0.0)
        if not suggestions.exists():
            self.stdout.write("No suggestions found.")
            return
        for s in suggestions.order_by("-created_at"):
            who = s.created_by.username if s.created_by else "anon"
            self.stdout.write(f"- {s.term} ({who} at {s.created_at.date()})")
