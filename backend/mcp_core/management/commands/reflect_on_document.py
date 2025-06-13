from django.core.management.base import BaseCommand
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from intel_core.models import Document


class Command(BaseCommand):
    """Reflect on a single document using the AssistantReflectionEngine."""

    help = "Reflect on a document and log a summary."

    def add_arguments(self, parser):
        parser.add_argument("--doc", required=True, help="Document id or slug")

    def handle(self, *args, **options):
        identifier = options["doc"]

        try:
            document = Document.objects.get(id=identifier)
        except Document.DoesNotExist:
            try:
                document = Document.objects.get(slug=identifier)
            except Document.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Document '{identifier}' not found"))
                return

        assistant = AssistantReflectionEngine.get_reflection_assistant()
        engine = AssistantReflectionEngine(assistant)

        summary, _insights, _prompt = engine.reflect_on_document(document)
        if summary:
            self.stdout.write(self.style.SUCCESS(f"Reflected on {document.title}: {summary[:60]}"))
        else:
            self.stdout.write(self.style.WARNING(f"No summary generated for {document.title}"))

