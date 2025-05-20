import os
import sys
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from embeddings.document_services.chunking import generate_chunks, merge_and_score_chunks


def run_demo(text: str) -> None:
    chunks = generate_chunks(text, chunk_size=200)
    print(f"Generated {len(chunks)} raw chunks")
    scored = merge_and_score_chunks(chunks, small_threshold=50, max_total_tokens=200)
    for i, (chunk, score, notes) in enumerate(scored, 1):
        keep = "✅" if score >= 0.5 else "❌"
        print(f"\n--- Chunk {i} ({keep}, score={score}) ---")
        if notes:
            print(f"Note: {notes}")
        print(chunk)


if __name__ == "__main__":
    sample = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "This is a sample document."
    run_demo(sample)
