import json
from django.core.management.base import BaseCommand
from assistants.utils.resolve import resolve_assistant
from assistants.utils.chunk_retriever import get_rag_chunk_debug
from assistants.models.diagnostics import AssistantDiagnosticReport
from memory.models import RAGGroundingLog
from intel_core.models import DocumentChunk
from django.utils import timezone


class Command(BaseCommand):
    """Run RAG regression tests defined in rag_tests.json."""

    help = "Execute RAG regression tests for an assistant"

    def add_arguments(self, parser):
        parser.add_argument(
            "--assistant",
            required=True,
            help="Assistant slug",
        )
        parser.add_argument(
            "--file",
            default="rag_tests.json",
            help="Path to rag_tests.json",
        )
        parser.add_argument("--save", action="store_true")

    def handle(self, *args, **options):
        slug = options["assistant"]
        file_path = options["file"]
        save_flag = options.get("save")
        assistant = resolve_assistant(slug)
        if not assistant:
            msg = self.style.ERROR(f"Assistant '{slug}' not found")
            self.stdout.write(msg)
            return
        try:
            with open(file_path) as f:
                data = json.load(f)
        except FileNotFoundError:
            msg = self.style.ERROR(f"File '{file_path}' not found")
            self.stdout.write(msg)
            return
        except json.JSONDecodeError as exc:
            msg = self.style.ERROR(f"Invalid JSON in '{file_path}': {exc}")
            self.stdout.write(msg)
            return

        if isinstance(data, list):
            tests = data
        else:
            tests = data.get("tests", [])
        passed = 0
        for t in tests:
            q = t.get("question")
            expected_id = (
                str(t.get("expected_chunk_id"))
                if t.get("expected_chunk_id") is not None
                else None
            )
            min_score = t.get("min_score", 0.0)
            expected_anchor = t.get("expected_anchor")

            info = get_rag_chunk_debug(str(assistant.id), q)
            score = info.get("retrieval_score") or 0.0
            top = info.get("matched_chunks", [])
            top = top[0] if top else None
            chunk_id = top.get("chunk_id") if top else None
            anchors = []
            if top:
                if top.get("anchor_slug"):
                    anchors.append(top["anchor_slug"])
                anchors.extend(top.get("matched_anchors", []))
            ok = True
            if expected_id and chunk_id != str(expected_id):
                ok = False
            if score < min_score:
                ok = False
            if expected_anchor and expected_anchor not in anchors:
                ok = False
            status = "PASS" if ok else "FAIL"
            self.stdout.write(f"[{status}] {q}")
            if ok:
                passed += 1
        total = len(tests)
        self.stdout.write(self.style.SUCCESS(f"{passed}/{total} tests passed"))

        logs = RAGGroundingLog.objects.filter(assistant=assistant)
        total_logs = logs.count() or 1
        fallback_rate = logs.filter(fallback_triggered=True).count() / total_logs
        glossary_rate = logs.filter(glossary_hits__len__gt=0).count() / total_logs
        chunk_total = DocumentChunk.objects.filter(document__memory_context=assistant.memory_context).count()

        if save_flag:
            AssistantDiagnosticReport.objects.create(
                assistant=assistant,
                slug=f"{assistant.slug}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                fallback_rate=fallback_rate,
                glossary_success_rate=glossary_rate,
                avg_chunk_score=0.0,
                rag_logs_count=total_logs,
                summary_markdown=f"Pass rate: {passed}/{total}",
            )
