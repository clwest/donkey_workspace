import os
import sys
import django

# Setup Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from memory.models import SymbolicMemoryAnchor

ANCHORS = [
    {"slug": "smart-contract", "label": "Smart Contract", "description": "Self-executing code on the blockchain", "is_focus_term": True},
    {"slug": "solidity", "label": "Solidity", "description": "Primary language for Ethereum smart contracts"},
    {"slug": "bytecode", "label": "Bytecode", "description": "Low level representation of compiled smart contracts"},
    {"slug": "evm", "label": "Ethereum Virtual Machine", "description": "Runtime environment for smart contracts", "is_focus_term": True},
    {"slug": "zk-rollup", "label": "ZK-Rollup", "description": "Layer 2 scaling technique leveraging zero-knowledge proofs", "is_focus_term": True},
    {"slug": "abi", "label": "Application Binary Interface (ABI)", "description": "Interface for interacting with compiled contracts"},
    {"slug": "compiler", "label": "Solidity Compiler", "description": "Tool that converts Solidity into bytecode"},
    {"slug": "deployment", "label": "Contract Deployment", "description": "Process of publishing compiled bytecode to the blockchain"},
]


def run():
    created = 0
    for data in ANCHORS:
        anchor, was_created = SymbolicMemoryAnchor.objects.get_or_create(
            slug=data["slug"],
            defaults={
                "label": data.get("label", data["slug"]),
                "description": data.get("description", ""),
                "is_focus_term": data.get("is_focus_term", False),
            },
        )
        if was_created:
            created += 1
            print(f"✅ Added anchor {anchor.slug}")
    print(f"🌱 Seeded {created} new anchors.")


if __name__ == "__main__":
    run()
