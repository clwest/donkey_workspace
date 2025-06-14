from django.core.management.base import BaseCommand
from django.core.management import call_command
from intel_core.models import Document

class Command(BaseCommand):
    help = "Retry document reflections for docs missing summaries"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=False, help="Assistant slug or id")

    def handle(self, *args, **options):
        assistant = options.get("assistant")
        qs = Document.objects.filter(summary__isnull=True)
        if assistant:
            qs = qs.filter(assistants__slug=assistant) | qs.filter(assigned_assistants__slug=assistant)
        for doc in qs.distinct():
            call_command("reflect_on_document", "--doc", str(doc.id), *( ["--assistant", assistant] if assistant else []))
            self.stdout.write(f"Reflected on {doc.title}")

