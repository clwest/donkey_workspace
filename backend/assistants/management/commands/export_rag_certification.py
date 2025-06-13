import json
from io import StringIO
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone
from pathlib import Path
from django.db import models
from assistants.utils.resolve import resolve_assistant
from intel_core.models import Document, DocumentChunk
from memory.models import SymbolicMemoryAnchor, RAGGroundingLog
from embeddings.models import EmbeddingDriftLog


class Command(BaseCommand):
    help = "Export RAG certification report for an assistant"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True, help="Assistant slug")

    def handle(self, *args, **options):
        slug = options["assistant"]
        assistant = resolve_assistant(slug)
        if not assistant:
            self.stdout.write(self.style.ERROR(f"Assistant '{slug}' not found"))
            return

        docs = Document.objects.filter(memory_context=assistant.memory_context).count()
        chunks = DocumentChunk.objects.filter(document__memory_context=assistant.memory_context).count()
        anchors = SymbolicMemoryAnchor.objects.count()

        buf = StringIO()
        call_command("run_rag_tests", "--assistant", slug, stdout=buf)
        result_line = buf.getvalue().splitlines()[-1] if buf.getvalue() else ""

        fallback_summary = list(
            RAGGroundingLog.objects.filter(assistant=assistant, fallback_triggered=True)
            .values("fallback_reason")
            .annotate(count=models.Count("id"))
        )

        drifts = list(
            EmbeddingDriftLog.objects.filter(assistant=assistant)
            .order_by("-timestamp")[:3]
            .values("timestamp", "mismatched_count", "orphaned_count")
        )

        data = {
            "assistant_name": assistant.name,
            "slug": assistant.slug,
            "uuid": str(assistant.id),
            "docs": docs,
            "chunks": chunks,
            "anchors": anchors,
            "retrieval_tests": result_line,
            "glossary_fallback_summary": fallback_summary,
            "drift_logs": drifts,
            "certified_at": timezone.now().isoformat(),
            "version": "Ω.10.1",
        }

        export_dir = Path("backend/exports/certifications")
        export_dir.mkdir(parents=True, exist_ok=True)
        json_path = export_dir / f"{assistant.slug}_rag_cert.json"
        md_path = export_dir / f"{assistant.slug}_rag_cert.md"
        public_dir = Path("static/rag_reports")
        public_dir.mkdir(parents=True, exist_ok=True)
        public_md = public_dir / f"{assistant.slug}.md"
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
        with open(md_path, "w") as f:
            f.write(f"# RAG Certification for {assistant.name}\n\n")
            for k, v in data.items():
                f.write(f"- **{k}**: {v}\n")
        with open(public_md, "w") as f:
            f.write(f"# RAG Metrics for {assistant.name}\n\n")
            f.write(f"- Chunk count: {chunks}\n")
            f.write(f"- Anchors: {anchors}\n")
            f.write(f"- Test Results: {result_line}\n")
            for item in fallback_summary:
                f.write(f"- {item['fallback_reason']}: {item['count']}\n")

        assistant.last_rag_certified_at = timezone.now()
        assistant.save(update_fields=["last_rag_certified_at"])

        self.stdout.write(self.style.SUCCESS(f"Certification exported to {md_path}"))
