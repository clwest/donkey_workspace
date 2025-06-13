from collections import Counter

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from assistants.models import Assistant
from assistants.models.reflection import AssistantReflectionLog
from assistants.models.thoughts import AssistantThoughtLog
from memory.models import MemoryEntry, SymbolicMemoryAnchor
from intel_core.utils.infer_anchors_from_memory import _tokenize

try:  # optional helper
    from assistants.utils.chunk_retriever import get_glossary_terms_from_reflections
except Exception:  # pragma: no cover - optional import
    get_glossary_terms_from_reflections = None


class Command(BaseCommand):
    """Infer glossary anchors from assistant memory, reflections or thoughts."""

    help = "Infer glossary anchors from assistant data"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True, type=str)
        parser.add_argument(
            "--source",
            choices=["memory", "reflections", "thoughts"],
            default="memory",
            help="Content source to parse",
        )

    def handle(self, *args, **options):
        slug = options["assistant"]
        source = options["source"]

        assistant = (
            Assistant.objects.filter(id=slug).first()
            or Assistant.objects.filter(slug=slug).first()
            or Assistant.objects.filter(memory_context_id=slug).first()
        )
        if not assistant:
            self.stderr.write(self.style.ERROR(f"Assistant '{slug}' not found"))
            return

        texts: list[str] = []
        if source == "reflections":
            if get_glossary_terms_from_reflections:
                ctx_id = str(assistant.memory_context_id) if assistant.memory_context_id else None
                texts.extend(get_glossary_terms_from_reflections(ctx_id))
            reflections = (
                AssistantReflectionLog.objects.filter(assistant=assistant)
                .order_by("-created_at")[:50]
            )
            texts.extend([r.summary or r.title or "" for r in reflections])
            doc_mems = (
                MemoryEntry.objects.filter(assistant=assistant, document__isnull=False)
                .order_by("-created_at")[:50]
            )
            for mem in doc_mems:
                if mem.summary:
                    texts.append(mem.summary)
                if mem.event:
                    texts.append(mem.event)
        elif source == "thoughts":
            thoughts = (
                AssistantThoughtLog.objects.filter(assistant=assistant)
                .order_by("-created_at")[:50]
            )
            texts.extend([t.thought or "" for t in thoughts])
        else:
            memories = (
                MemoryEntry.objects.filter(assistant=assistant)
                .order_by("-created_at")[:100]
            )
            for mem in memories:
                if mem.summary:
                    texts.append(mem.summary)
                if mem.event:
                    texts.append(mem.event)
                texts.extend(list(mem.tags.values_list("slug", flat=True)))

        if not texts:
            self.stdout.write(
                self.style.WARNING(
                    f"No text found to analyze for assistant {assistant.slug}. Skipping."
                )
            )
            return

        counter: Counter[str] = Counter()
        for txt in texts:
            counter.update(_tokenize(txt))

        seen = set()

        created = 0
        for term in sorted(counter.keys()):
            if len(term) < 4:
                continue
            slug_term = slugify(term)
            if slug_term in seen:
                continue
            if SymbolicMemoryAnchor.objects.filter(slug=slug_term).exists():
                continue
            if SymbolicMemoryAnchor.objects.filter(label__iexact=term, mutation_status="rejected").exists():
                continue
            SymbolicMemoryAnchor.objects.create(
                slug=slug_term,
                label=term.title(),
                mutation_status="pending",
                mutation_source="assistant_memory_inferred",
                assistant=assistant,
                memory_context=assistant.memory_context,
                suggested_by="gpt-4o",
                source="reflection" if source == "reflections" else "inferred",
                created_from="assistant_memory",
            )
            created += 1
            seen.add(slug_term)

        self.stdout.write(self.style.SUCCESS(f"Saved {created} anchors from {source}"))
