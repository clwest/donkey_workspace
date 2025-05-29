"""Append RAG failure details to rag_failure_log.json."""

import json
import os
import sys
from pathlib import Path
from django.utils import timezone
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

LOG_PATH = Path(__file__).resolve().parent / "rag_failure_log.json"


def update_failure_log(assistant_slug: str, query: str, chunk_ids: list[str], scores: list[float], reflection: str = "", message: str = "") -> dict:
    """Append a new failure entry using array fields."""
    if LOG_PATH.exists():
        with open(LOG_PATH) as f:
            data = json.load(f)
    else:
        data = []

    entry = {
        "assistant": assistant_slug,
        "query": query,
        "chunk_ids": chunk_ids,
        "scores": scores,
        "reflection": reflection,
        "message": message,
        "timestamp": timezone.now().isoformat(),
    }
    data.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)
    return entry


def main(argv: list[str]):
    if len(argv) < 4:
        print(
            "Usage: python update_rag_failure_log.py <assistant> <query> <chunk_ids> <scores> [reflection] [message]"
        )
        return

    assistant = argv[0]
    query = argv[1]
    chunk_ids = argv[2].split(",") if argv[2] else []
    scores = [float(s) for s in argv[3].split(",") if s]
    reflection = argv[4] if len(argv) > 4 else ""
    message = argv[5] if len(argv) > 5 else ""

    entry = update_failure_log(assistant, query, chunk_ids, scores, reflection, message)
    print(f"Logged failure entry for {entry['assistant']} with {len(entry['chunk_ids'])} chunks")


if __name__ == "__main__":
    main(sys.argv[1:])
