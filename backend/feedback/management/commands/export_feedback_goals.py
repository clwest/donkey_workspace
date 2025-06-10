from django.core.management.base import BaseCommand
from feedback.models import FeedbackEntry
from pathlib import Path


class Command(BaseCommand):
    help = "Export feedback into GOALS.md"

    def handle(self, *args, **options):
        items = FeedbackEntry.objects.all().order_by('-created_at')
        lines = ["## 📝 User Feedback", ""]
        for fb in items:
            lines.append(f"- [ ] ({fb.category}) {fb.description} ({fb.assistant_slug})")
        path = Path('GOALS.md')
        content = path.read_text().rstrip() + "\n\n" + "\n".join(lines) + "\n"
        path.write_text(content)
        self.stdout.write(self.style.SUCCESS('Feedback exported to GOALS.md'))
