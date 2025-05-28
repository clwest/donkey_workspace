from memory.models import SymbolicMemoryAnchor

glossary_terms = [
    {
        "slug": "zk-rollup",
        "label": "ZK-Rollup",
        "description": "A type of Layer 2 scaling solution that uses zero-knowledge proofs to bundle many transactions into one, reducing cost and improving scalability on blockchains like Ethereum.",
    },
    {
        "slug": "ethereum-virtual-machine",
        "label": "Ethereum Virtual Machine",
        "description": "The EVM is the runtime environment for smart contracts in Ethereum. It enables code execution and state transitions on the blockchain.",
    },
]

for term in glossary_terms:
    SymbolicMemoryAnchor.objects.update_or_create(
        slug=term["slug"],
        defaults={
            "label": term["label"],
            "description": term["description"],
            "is_focus_term": True,
        },
    )