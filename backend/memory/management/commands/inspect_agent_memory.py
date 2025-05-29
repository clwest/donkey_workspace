from django.core.management.base import BaseCommand
from agents.models import Agent
from assistants.models import Assistant
from intel_core.models import Document, DocumentChunk
from memory.models import SymbolicMemoryAnchor
from utils.inspection_helpers import bool_icon
from difflib import SequenceMatcher


class Command(BaseCommand):
    """Inspect agent memory chunks and anchor coverage."""

    help = "Inspect agent memory and glossary coverage"

    def add_arguments(self, parser):
        parser.add_argument(
            "--agent",
            action="append",
            help="Agent slug to inspect. Can be repeated.",
        )
        parser.add_argument(
            "--assistant",
            action="append",
            help="Assistant slug to inspect (alias of --agent).",
        )
        parser.add_argument("--slug", help="Filter by anchor slug")
        parser.add_argument("--doc", help="Filter by partial document title")
        parser.add_argument("--min-score", type=float, default=0.75)
        parser.add_argument(
            "--glossary-only", action="store_true", help="Only include glossary chunks"
        )

    def handle(self, *args, **options):
        agent_slugs = options.get("agent") or []
        assistant_slugs = options.get("assistant") or []
        slug = options.get("slug")
        doc_title = options.get("doc")
        min_score = options.get("min_score", 0.75)
        glossary_only = options.get("glossary_only", False)

        all_slugs = agent_slugs + assistant_slugs

        agents = []
        assistants = []

        if all_slugs:
            for s in all_slugs:
                try:
                    assistants.append(Assistant.objects.get(slug=s))
                    continue
                except Assistant.DoesNotExist:
                    pass
                try:
                    agents.append(Agent.objects.get(slug=s))
                    continue
                except Agent.DoesNotExist:
                    possible = list(Assistant.objects.values_list("slug", flat=True)) + list(
                        Agent.objects.values_list("slug", flat=True)
                    )
                    suggestions = [p for p in possible if SequenceMatcher(None, s, p).ratio() > 0.6]
                    msg = f"No assistant/agent found for slug '{s}'."
                    if suggestions:
                        msg += " Suggestions: " + ", ".join(suggestions)
                    self.stdout.write(self.style.ERROR(msg))

        if not all_slugs:
            agents = list(Agent.objects.all())

        anchors = SymbolicMemoryAnchor.objects.all()
        if slug:
            anchors = anchors.filter(slug=slug)

        if not agents and not assistants:
            self.stdout.write(self.style.ERROR("No matching agents or assistants."))
            return

        def inspect_entity(entity, is_assistant: bool) -> None:
            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    f"{'Assistant' if is_assistant else 'Agent'}: {entity.name} ({entity.slug})"
                )
            )
            documents = entity.documents.all() if is_assistant else entity.trained_documents.all()
            if doc_title:
                documents = documents.filter(title__icontains=doc_title)
            doc_ids = list(documents.values_list("id", flat=True))
            if not doc_ids:
                matches = []
                if doc_title:
                    matches = list(
                        Document.objects.filter(title__icontains=doc_title).values_list("title", flat=True)[:5]
                    )
                if matches:
                    self.stdout.write("  No documents found. Did you mean:")
                    for m in matches:
                        self.stdout.write(f"    - {m}")
                else:
                    self.stdout.write("  No documents found for criteria")
                return

            chunks = (
                DocumentChunk.objects.filter(document_id__in=doc_ids)
                .select_related("anchor", "document", "embedding")
            )
            if slug:
                chunks = chunks.filter(anchor__slug=slug)
            if glossary_only:
                chunks = chunks.filter(is_glossary=True)

            total = chunks.count()
            glossary_count = chunks.filter(is_glossary=True).count()
            self.stdout.write(f"  Total Chunks: {total} | Glossary: {glossary_count}")

            if doc_title:
                self.stdout.write("  📚 Anchor Summary:")
                for anchor in anchors:
                    count = chunks.filter(anchor=anchor).count()
                    gloss = chunks.filter(anchor=anchor, is_glossary=True).count()
                    self.stdout.write(
                        f"    {anchor.slug:<25} {count} chunks | glossary={gloss}"
                    )

            used = chunks.filter(score__gte=min_score).order_by("-score")
            filtered = chunks.filter(score__lt=min_score).order_by("-score")

            if used.exists():
                self.stdout.write("  Used Chunks:")
                for ch in used:
                    preview = ch.text[:80].replace("\n", " ")
                    self.stdout.write(
                        f"    {ch.id} | {ch.score:.2f} | {preview} | anchor={getattr(ch.anchor,'slug',None)} | glossary={ch.is_glossary} | emb={getattr(ch.embedding,'embedding_id',None)}"
                    )

            if filtered.exists():
                self.stdout.write("  Filtered Out:")
                for ch in filtered:
                    preview = ch.text[:80].replace("\n", " ")
                    self.stdout.write(
                        f"    {ch.id} | {ch.score:.2f} | {preview} | anchor={getattr(ch.anchor,'slug',None)} | glossary={ch.is_glossary} | emb={getattr(ch.embedding,'embedding_id',None)}"
                    )

        for a in assistants:
            inspect_entity(a, True)
        for ag in agents:
            inspect_entity(ag, False)

