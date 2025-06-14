import json
from django.core.management.base import BaseCommand
from assistants.utils.resolve import resolve_assistant
from assistants.utils.chunk_retriever import get_rag_chunk_debug
from assistants.models.diagnostics import AssistantDiagnosticReport
from memory.models import RAGGroundingLog
from utils.rag_debug import log_rag_debug
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
        parser.add_argument("--log-scores", action="store_true")

    def handle(self, *args, **options):
        slug = options["assistant"]
        file_path = options["file"]
        save_flag = options.get("save")
        log_scores = options.get("log_scores")
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
        score_log = []
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
            else:
                chunk_ids = [c.get("chunk_id") for c in info.get("matched_chunks", []) + info.get("fallback_chunks", [])]
                if expected_anchor and expected_anchor not in anchors:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Missed anchor {expected_anchor} score={score:.2f} chunks={', '.join(chunk_ids)}"
                        )
                    )
                    try:
                        log_rag_debug(
                            assistant,
                            q,
                            {
                                "used_chunks": info.get("matched_chunks", []) + info.get("fallback_chunks", []),
                                "rag_fallback": info.get("fallback_triggered", False),
                                "fallback_reason": info.get("reason"),
                                "anchor_hits": anchors,
                                "anchor_misses": [expected_anchor],
                                "retrieval_score": score,
                                "fallback_chunk_scores": [
                                    info["scores"].get(cid, 0.0) for cid in chunk_ids
                                ],
                            },
                            debug=True,
                            expected_anchor=expected_anchor,
                        )
                    except Exception:
                        pass
            score_log.append(
                {
                    "question": q,
                    "expected_anchor": expected_anchor,
                    "retrieval_score": score,
                    "chunks": info.get("matched_chunks", []) + info.get("fallback_chunks", []),
                    "scores": info.get("scores", {}),
                    "glossary_misses": info.get("glossary_misses", []),
                }
            )
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

        if log_scores:
            out = {"assistant": assistant.slug, "results": score_log}
            self.stdout.write(json.dumps(out, indent=2))
