from django.core.management.base import BaseCommand
from agents.models import Agent
from intel_core.models import DocumentChunk
from memory.models import SymbolicMemoryAnchor
from utils.inspection_helpers import bool_icon


class Command(BaseCommand):
    """Inspect agent memory chunks and anchor coverage."""

    help = "Inspect agent memory and glossary coverage"

    def add_arguments(self, parser):
        parser.add_argument("--agent", action="append", help="Agent slug to inspect. Can be repeated.")
        parser.add_argument("--slug", help="Filter by anchor slug")
        parser.add_argument("--doc", help="Filter by partial document title")
        parser.add_argument("--min-score", type=float, default=0.75)
        parser.add_argument("--glossary-only", action="store_true", help="Only include glossary chunks")

    def handle(self, *args, **options):
        agent_slugs = options.get("agent") or []
        slug = options.get("slug")
        doc_title = options.get("doc")
        min_score = options.get("min_score", 0.75)
        glossary_only = options.get("glossary_only", False)

        agents = Agent.objects.all()
        if agent_slugs:
            agents = agents.filter(slug__in=agent_slugs)

        anchors = SymbolicMemoryAnchor.objects.all()
        if slug:
            anchors = anchors.filter(slug=slug)

        if not agents.exists():
            self.stdout.write(self.style.ERROR("No matching agents."))
            return

        for agent in agents:
            self.stdout.write(self.style.MIGRATE_HEADING(f"Agent: {agent.name} ({agent.slug})"))
            documents = agent.trained_documents.all()
            if doc_title:
                documents = documents.filter(title__icontains=doc_title)
            doc_ids = list(documents.values_list("id", flat=True))
            if not doc_ids:
                self.stdout.write("  No documents found for criteria")
                continue

            chunks = DocumentChunk.objects.filter(document_id__in=doc_ids).select_related("anchor", "document")
            if slug:
                chunks = chunks.filter(anchor__slug=slug)
            if glossary_only:
                chunks = chunks.filter(is_glossary=True)

            total = chunks.count()
            glossary_count = chunks.filter(is_glossary=True).count()
            self.stdout.write(f"  Total Chunks: {total} | Glossary: {glossary_count}")

            for anchor in anchors:
                count = chunks.filter(anchor=anchor).count()
                self.stdout.write(f"  {anchor.slug:<15} {bool_icon(count>0)} ({count})")

            used = chunks.filter(score__gte=min_score).order_by("-score")
            filtered = chunks.filter(score__lt=min_score).order_by("-score")

            if used.exists():
                self.stdout.write("  Used Chunks:")
                for ch in used:
                    preview = ch.text[:80].replace("\n", " ")
                    self.stdout.write(
                        f"    {ch.score:.2f} | {ch.document.title} | {preview} | anchor={getattr(ch.anchor,'slug',None)}"
                    )

            if filtered.exists():
                self.stdout.write("  Filtered Out:")
                for ch in filtered:
                    preview = ch.text[:80].replace("\n", " ")
                    self.stdout.write(
                        f"    {ch.score:.2f} | {ch.document.title} | {preview} | anchor={getattr(ch.anchor,'slug',None)}"
                    )

