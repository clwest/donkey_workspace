from django.core.management.base import BaseCommand
from memory.models import SymbolicMemoryAnchor

DEFAULT_ANCHORS = [
    {"slug": "mcp", "label": "MCP", "description": "Memory Continuity Protocol"},
    {"slug": "sdk", "label": "SDK", "description": "Software Development Kit"},
    {"slug": "rag", "label": "RAG", "description": "Retrieval-Augmented Generation"},
    {"slug": "glossary", "label": "Glossary"},
    {"slug": "fork", "label": "Fork"},
    {"slug": "fallback", "label": "Fallback"},
    {"slug": "hallucination", "label": "Hallucination"},
    {"slug": "ritual", "label": "Ritual"},
    {"slug": "summon", "label": "Summon"},
    {"slug": "zk-rollup", "label": "ZK-Rollup"},
    {"slug": "evm", "label": "Ethereum Virtual Machine"},
]


class Command(BaseCommand):
    help = "Seed default SymbolicMemoryAnchor records"

    def handle(self, *args, **options):
        created = 0
        for data in DEFAULT_ANCHORS:
            anchor, was_created = SymbolicMemoryAnchor.objects.get_or_create(
                slug=data["slug"], defaults={"label": data.get("label", data["slug"]), "description": data.get("description", "")}
            )
            if was_created:
                created += 1
                self.stdout.write(f"Added anchor {anchor.slug}")
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} anchors."))
