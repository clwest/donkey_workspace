from django.core.management.base import BaseCommand
from mcp_core.models import DevDoc
from intel_core.models import Document
from assistants.models.reflection import AssistantReflectionLog
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from mcp_core.utils.devdoc_tools import link_document_to_devdoc, create_summary_from_doc
from devtools.models import DevLog


class Command(BaseCommand):
    help = "Audit DevDocs, repair document links, and ensure reflections exist."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reflect", action="store_true", help="Generate reflections when missing"
        )

    def handle(self, *args, **options):
        reflect_missing = options["reflect"]
        processed = 0
        relinked = 0
        reflections = 0

        reflection_assistant = None
        if reflect_missing:
            reflection_assistant = AssistantReflectionEngine.get_reflection_assistant()
            engine = AssistantReflectionEngine(reflection_assistant)

        for devdoc in DevDoc.objects.all():
            processed += 1
            document = devdoc.linked_document
            if not document:
                document = Document.objects.filter(slug=devdoc.slug).first()
                if not document:
                    document = Document.objects.create(
                        title=devdoc.title,
                        slug=devdoc.slug,
                        content=devdoc.content,
                        source="devdoc",
                        source_type="markdown",
                    )
                    self.stdout.write(f"📄 Created document {document.slug}")
                relinked += 1
                link_document_to_devdoc(devdoc, document)
            else:
                if document.title != devdoc.title:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Title mismatch for {devdoc.slug}: '{devdoc.title}' vs '{document.title}'"
                        )
                    )
            create_summary_from_doc(document)

            if not AssistantReflectionLog.objects.filter(document=document).exists():
                if reflect_missing:
                    summary, _insights, _prompt = engine.reflect_on_document(document)
                    if summary:
                        reflections += 1
                        DevLog.objects.create(
                            event="relink_devdocs.reflect",
                            assistant=reflection_assistant,
                            details=f"Reflected on {document.slug}",
                        )
                        self.stdout.write(f"📝 Reflected on {document.slug}")
                else:
                    self.stdout.write(
                        self.style.WARNING(f"No reflection for {document.slug}")
                    )

        self.stdout.write(self.style.SUCCESS(f"Processed {processed} DevDocs"))
        self.stdout.write(self.style.SUCCESS(f"Relinked {relinked}"))
        if reflect_missing:
            self.stdout.write(self.style.SUCCESS(f"Reflections created {reflections}"))
