from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone
from pathlib import Path
from django.conf import settings
from django.db.models import Avg
from assistants.models import Assistant
from assistants.models.diagnostics import AssistantDiagnosticReport
from memory.models import RAGGroundingLog, RAGDiagnosticLog


class Command(BaseCommand):
    """Generate persistent RAG diagnostic reports for public assistants."""

    help = "Create AssistantDiagnosticReport records and markdown summaries"

    def add_arguments(self, parser):
        parser.add_argument("--markdown-only", action="store_true")

    def handle(self, *args, **options):
        markdown_only = options.get("markdown_only", False)
        out_dir = Path(settings.BASE_DIR) / "static" / "diagnostics"
        out_dir.mkdir(parents=True, exist_ok=True)
        for assistant in Assistant.objects.filter(is_demo=True):
            if not markdown_only:
                call_command("run_rag_tests", "--assistant", assistant.slug)
            ground = RAGGroundingLog.objects.filter(assistant=assistant)
            diag = RAGDiagnosticLog.objects.filter(assistant=assistant)
            total = ground.count() or 1
            fallback_rate = ground.filter(fallback_triggered=True).count() / total
            glossary_success_rate = (
                ground.filter(glossary_hits__len__gt=0).count() / total
            )
            avg_chunk_score = (
                diag.aggregate(avg=Avg("confidence_score_avg"))["avg"] or 0.0
            )
            rag_logs_count = total
            summary = (
                f"# Diagnostic Report for {assistant.name}\n\n"
                f"- Fallback rate: {fallback_rate*100:.1f}%\n"
                f"- Glossary success rate: {glossary_success_rate*100:.1f}%\n"
                f"- Average chunk score: {avg_chunk_score:.2f}\n"
                f"- Total logs: {rag_logs_count}\n"
            )
            report = AssistantDiagnosticReport.objects.create(
                assistant=assistant,
                slug=f"{assistant.slug}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                fallback_rate=fallback_rate,
                glossary_success_rate=glossary_success_rate,
                avg_chunk_score=avg_chunk_score,
                rag_logs_count=rag_logs_count,
                summary_markdown=summary,
            )
            if (
                fallback_rate < 0.10
                and glossary_success_rate > 0.30
            ):
                assistant.certified_rag_ready = True
                assistant.rag_certification_date = timezone.now()
                assistant.save(update_fields=["certified_rag_ready", "rag_certification_date"])
            with open(out_dir / f"{assistant.slug}.md", "w") as f:
                f.write(summary)
            self.stdout.write(
                self.style.SUCCESS(
                    f"{assistant.slug}: {fallback_rate:.2f} fallback, {glossary_success_rate:.2f} glossary"
                )
            )
