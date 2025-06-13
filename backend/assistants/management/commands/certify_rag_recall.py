from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db.models import Avg
from django.utils import timezone

from assistants.models import Assistant
from assistants.models.diagnostics import AssistantDiagnosticReport
from memory.models import RAGGroundingLog, RAGDiagnosticLog
from intel_core.models import DocumentChunk

class Command(BaseCommand):
    help = "Run RAG tests for assistants and record certification status"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Assistant slug", default=None)

    def handle(self, *args, **options):
        slug = options.get("assistant")
        assistants = (
            [Assistant.objects.get(slug=slug)] if slug else list(Assistant.objects.all())
        )
        for assistant in assistants:
            call_command("run_rag_tests", "--assistant", assistant.slug, "--save")
            ground = RAGGroundingLog.objects.filter(assistant=assistant)
            diag = RAGDiagnosticLog.objects.filter(assistant=assistant)
            total = ground.count() or 1
            fallback_rate = ground.filter(fallback_triggered=True).count() / total
            glossary_hits = ground.filter(glossary_hits__len__gt=0).count()
            glossary_rate = glossary_hits / total
            avg_score = diag.aggregate(avg=Avg("confidence_score_avg"))["avg"] or 0.0
            chunk_count = DocumentChunk.objects.filter(document__linked_assistants=assistant, embedding_status="embedded").count()
            AssistantDiagnosticReport.objects.create(
                assistant=assistant,
                slug=f"{assistant.slug}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                fallback_rate=fallback_rate,
                glossary_success_rate=glossary_rate,
                avg_chunk_score=avg_score,
                rag_logs_count=total,
                summary_markdown=f"Avg:{avg_score:.2f} Glossary:{glossary_rate:.2f} Fallback:{fallback_rate:.2f}",
            )
            certified = (
                assistant.documents.exists()
                and chunk_count >= 10
                and avg_score >= 0.25
                and glossary_hits >= 2
                and fallback_rate <= 0.25
            )
            assistant.rag_certified = certified
            assistant.last_rag_certified_at = timezone.now()
            assistant.save(update_fields=["rag_certified", "last_rag_certified_at"])
            status = "✅" if certified else "❌"
            self.stdout.write(
                f"{status} {assistant.slug}: chunks={chunk_count} score={avg_score:.2f} glossary={glossary_hits} fallback={fallback_rate:.2f}"
            )
