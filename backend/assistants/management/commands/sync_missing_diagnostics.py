from django.core.management.base import BaseCommand
from django.core.management import call_command
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor
from assistants.models.reflection import AssistantReflectionLog


class Command(BaseCommand):
    """Backfill glossary anchors and diagnostics for unhealthy assistants."""

    help = "Sync missing diagnostics for assistants"

    def handle(self, *args, **options):
        assistants = Assistant.objects.all()
        for a in assistants:
            missing_anchor = not SymbolicMemoryAnchor.objects.filter(
                assistant=a
            ).exists()
            missing_refl = not AssistantReflectionLog.objects.filter(
                assistant=a
            ).exists()
            if missing_anchor or missing_refl:
                self.stdout.write(f"Syncing {a.slug}...")
                if missing_anchor:
                    call_command("infer_glossary_anchors", "--assistant", a.slug)
                if missing_refl:
                    for doc in a.documents.all():
                        call_command(
                            "reflect_on_document",
                            "--doc",
                            str(doc.id),
                            "--assistant",
                            a.slug,
                        )
                call_command("generate_diagnostic_reports", "--markdown-only")
                call_command("run_rag_tests", "--assistant", a.slug)
