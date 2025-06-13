from django.core.management.base import BaseCommand
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from intel_core.models import Document


class Command(BaseCommand):
    """Reflect on a single document using the AssistantReflectionEngine."""

    help = "Reflect on a document and log a summary."

    def add_arguments(self, parser):
        parser.add_argument("--doc", required=True, help="Document id or slug")
        parser.add_argument(
            "--assistant",
            required=False,
            help="Assistant slug or id to scope the reflection",
        )

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

        assistant_id = options.get("assistant")
        if assistant_id:
            try:
                from assistants.models import Assistant

                assistant = Assistant.objects.get(id=assistant_id)
            except Assistant.DoesNotExist:
                assistant = Assistant.objects.filter(slug=assistant_id).first()
                if not assistant:
                    self.stderr.write(
                        self.style.ERROR(
                            f"Assistant '{assistant_id}' not found, using default"
                        )
                    )
                    assistant = AssistantReflectionEngine.get_reflection_assistant()
        else:
            assistant = AssistantReflectionEngine.get_reflection_assistant()
        engine = AssistantReflectionEngine(assistant)

        summary, _insights, _prompt = engine.reflect_on_document(document)
        if summary:
            self.stdout.write(self.style.SUCCESS(f"Reflected on {document.title}: {summary[:60]}"))
        else:
            self.stdout.write(self.style.WARNING(f"No summary generated for {document.title}"))

