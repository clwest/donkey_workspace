import re
from collections import Counter
from typing import List

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from assistants.utils.resolve import resolve_assistant
from intel_core.models import DocumentChunk
from intel_core.core.filters import ALL_STOP_WORDS
from memory.models import SymbolicMemoryAnchor, RAGGroundingLog

TOKEN_RE = re.compile(r"[a-zA-Z0-9-]{3,}")


def _tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(text.lower())


class Command(BaseCommand):
    """Suggest improved glossary anchors from weak RAG matches."""

    help = "Analyze RAGGroundingLog for weak matches and suggest better anchors"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True, type=str)
        parser.add_argument(
            "--score", type=float, default=0.25, help="Score threshold for weak matches"
        )
        parser.add_argument(
            "--radius", type=int, default=5, help="Chunk window radius for neighbors"
        )
        parser.add_argument("--auto-approve", action="store_true")

    def handle(self, *args, **options):
        assistant = resolve_assistant(options["assistant"])
        if not assistant:
            self.stderr.write(self.style.ERROR("Assistant not found"))
            return

        score_th = options["score"]
        radius = options["radius"]
        auto = options.get("auto_approve")

        logs = RAGGroundingLog.objects.filter(
            assistant=assistant,
            fallback_triggered=True,
            adjusted_score__lt=score_th,
        )
        if not logs.exists():
            self.stdout.write("No weak fallback matches found.")
            return

        existing = set(
            SymbolicMemoryAnchor.objects.filter(memory_context=assistant.memory_context)
            .values_list("slug", flat=True)
        )

        for log in logs:
            chunk_ids = [cid for cid in log.used_chunk_ids if cid]
            chunks = list(DocumentChunk.objects.filter(id__in=chunk_ids))
            texts = []
            for ch in chunks:
                texts.append(ch.text)
                neighbors = DocumentChunk.objects.filter(
                    document=ch.document,
                    order__gte=ch.order - radius,
                    order__lte=ch.order + radius,
                ).exclude(id=ch.id)
                texts.extend(n.text for n in neighbors if n.score > ch.score)
            if not texts:
                continue

            tokens = Counter()
            for t in _tokenize(" ".join(texts)):
                if t not in ALL_STOP_WORDS:
                    tokens[t] += 1

            candidates = [tok for tok, cnt in tokens.most_common() if cnt > 1]
            suggestions = [tok for tok in candidates if slugify(tok) not in existing]
            if not suggestions:
                continue
            self.stdout.write(
                f"{log.id} → suggested anchors: {', '.join(suggestions[:3])}"
            )
            if auto:
                for term in suggestions[:3]:
                    slug = slugify(term)
                    SymbolicMemoryAnchor.objects.get_or_create(
                        slug=slug,
                        defaults=dict(
                            label=term.title(),
                            source="rag_boost",
                            created_from="rag_boost",
                            suggested_by="rag_boost_engine",
                            assistant=assistant,
                            memory_context=assistant.memory_context,
                        ),
                    )
                    existing.add(slug)

