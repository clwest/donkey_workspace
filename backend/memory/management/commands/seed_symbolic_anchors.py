from django.core.management.base import BaseCommand
from memory.models import SymbolicMemoryAnchor

DEFAULT_ANCHORS = [
    {"slug": "mcp", "label": "MCP", "description": "Memory Continuity Protocol", "is_focus_term": True},
    {"slug": "sdk", "label": "SDK", "description": "Software Development Kit"},
    {"slug": "rag", "label": "RAG", "description": "Retrieval-Augmented Generation"},
    {"slug": "glossary", "label": "Glossary"},
    {"slug": "fork", "label": "Fork"},
    {"slug": "fallback", "label": "Fallback"},
    {"slug": "hallucination", "label": "Hallucination"},
    {"slug": "ritual", "label": "Ritual"},
    {"slug": "summon", "label": "Summon"},
    {"slug": "zk-rollup", "label": "ZK-Rollup", "is_focus_term": True},
    {"slug": "evm", "label": "Ethereum Virtual Machine", "is_focus_term": True},
    {
        "slug": "mythpath",
        "label": "MythPath",
        "tooltip": "Your assistant's journey and personality archetype.",
        "display_location": ["dashboard", "assistant_detail"],
        "display_tooltip": True,
    },
]


class Command(BaseCommand):
    help = "Seed default SymbolicMemoryAnchor records"

    def handle(self, *args, **options):
        created = 0
        for data in DEFAULT_ANCHORS:
            anchor, was_created = SymbolicMemoryAnchor.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "label": data.get("label", data["slug"]),
                    "description": data.get("description", ""),
                    "is_focus_term": data.get("is_focus_term", False),
                    "glossary_guidance": data.get("tooltip", ""),
                    "display_location": data.get("display_location", []),
                    "display_tooltip": data.get("display_tooltip", False),
                },
            )
            if was_created:
                created += 1
                self.stdout.write(f"Added anchor {anchor.slug}")
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} anchors."))
