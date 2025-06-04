import json
import hashlib
from pathlib import Path
from datetime import datetime

from django.core.management.base import BaseCommand

STATUS_FILE = Path("logs/template_status.json")


class Command(BaseCommand):
    help = "Inspect template health and detect drift"

    def add_arguments(self, parser):
        parser.add_argument(
            "--include-rag",
            action="store_true",
            help="Include templates linked to RAG renderers",
        )

    def handle(self, *args, **options):
        include_rag = options.get("include_rag", False)
        data = {}
        if STATUS_FILE.exists():
            data = json.loads(STATUS_FILE.read_text())
        output = []
        for path_str, info in data.items():
            path = Path(path_str)
            current_hash = None
            if path.exists():
                current_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            diff = current_hash != info.get("file_hash")
            if include_rag and not info.get("is_rag_linked"):
                continue
            output.append(
                {
                    "template_path": path_str,
                    "hash_diff": diff,
                    "tag_libraries": info.get("tag_libraries", []),
                    "rag_relevance": info.get("is_rag_linked", False),
                    "assistant_dependency_count": info.get(
                        "assistant_dependency_count", 0
                    ),
                }
            )
        self.stdout.write(json.dumps(output, indent=2))
