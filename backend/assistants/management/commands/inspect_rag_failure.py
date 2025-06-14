from django.core.management.base import BaseCommand
import json
from assistants.utils.resolve import resolve_assistant
from assistants.utils.chunk_retriever import get_rag_chunk_debug

class Command(BaseCommand):
    help = "Inspect RAG failures for an assistant"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True, help="Assistant slug")
        parser.add_argument(
            "--file", default="rag_tests.json", help="Path to rag_tests.json"
        )
        parser.add_argument(
            "--show-anchor-stats",
            action="store_true",
            help="Display anchor reliability metrics",
        )

    def handle(self, *args, **options):
        slug = options["assistant"]
        file_path = options["file"]
        assistant = resolve_assistant(slug)
        if not assistant:
            self.stdout.write(self.style.ERROR(f"Assistant '{slug}' not found"))
            return
        try:
            with open(file_path) as f:
                data = json.load(f)
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Failed to load '{file_path}': {exc}"))
            return
        tests = data if isinstance(data, list) else data.get("tests", [])
        missed = []
        suggestions = []
        show_stats = options.get("show_anchor_stats")
        for t in tests:
            q = t.get("question")
            expected = t.get("expected_anchor")
            info = get_rag_chunk_debug(str(assistant.id), q)
            chunks = info.get("matched_chunks", []) + info.get("fallback_chunks", [])
            anchors = []
            for c in chunks:
                if c.get("anchor_slug"):
                    anchors.append(c["anchor_slug"])
                anchors.extend(c.get("matched_anchors", []))
            hit = expected in anchors if expected else False
            score = info.get("retrieval_score", 0.0)
            chunk_ids = [c.get("chunk_id") for c in chunks]
            if expected and not hit:
                missed.append(expected)
                self.stdout.write(
                    self.style.WARNING(
                        f"[MISS] {q} -> {expected} score={score:.2f} chunks={', '.join(chunk_ids)}"
                    )
                )
            else:
                self.stdout.write(self.style.SUCCESS(f"[OK] {q}"))
            if show_stats and expected:
                from memory.models import SymbolicMemoryAnchor

                a = SymbolicMemoryAnchor.objects.filter(slug=expected).first()
                if a:
                    self.stdout.write(
                        f"  Anchor {a.slug} avg={a.avg_score:.2f} uses={a.total_uses} fallback={a.fallback_rate:.2f}"
                    )
            suggestions.extend(info.get("glossary_misses", []))
        if missed:
            self.stdout.write("\nMissed anchors: " + ", ".join(sorted(set(missed))))
        if suggestions:
            sugg = [s for s in set(suggestions) if s not in missed]
            if sugg:
                self.stdout.write("Possible anchors to add: " + ", ".join(sorted(sugg)))
