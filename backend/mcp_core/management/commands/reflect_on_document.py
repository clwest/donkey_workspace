from django.core.management.base import BaseCommand, CommandError
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from assistants.utils.assistant_lookup import resolve_assistant
from intel_core.models import Document
from mcp_core.models import DevDoc


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

        document = None
        try:
            document = Document.objects.filter(id=identifier).first()
        except (ValueError, Exception):
            document = None
        if not document:
            document = Document.objects.filter(slug=identifier).first()
        if not document:
            devdoc = (
                DevDoc.objects.filter(uuid=identifier).first()
                or DevDoc.objects.filter(slug=identifier).first()
            )
            if devdoc and devdoc.linked_document:
                document = devdoc.linked_document
        if not document:
            self.stderr.write(
                self.style.ERROR(f"Document or DevDoc '{identifier}' not found")
            )
            return

        assistant_id = options.get("assistant")
        if assistant_id:

            assistant = resolve_assistant(assistant_id)
            if not assistant:
                raise CommandError(f"Assistant '{assistant_id}' not found")
        else:
            assistant = AssistantReflectionEngine.get_reflection_assistant()
        if not assistant.memory_context_id:
            self.stderr.write(self.style.WARNING("Assistant has no memory context"))
        engine = AssistantReflectionEngine(assistant)

        summary, _insights, _prompt = engine.reflect_on_document(document)
        if summary:
            self.stdout.write(
                self.style.SUCCESS(f"Reflected on {document.title}: {summary[:60]}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"No summary generated for {document.title}")
            )
