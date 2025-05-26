import sys
import os
import django
import json

# Django setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from embeddings.helpers.helpers_similarity import get_similar_documents
from embeddings.helpers.helper_tagging import generate_tags_for_memory
from memory.models import MemoryEntry


def test_vector_query(query_text="How does the assistant handle memory reflection?"):
    print(f"🔍 Query: {query_text}\n")

    memory_log = {
        "query": query_text,
        "results": {}
    }

    domains = ["prompt", "assistantthoughtlog", "devdoc"]
    for domain in domains:
        print(f"=== Top Matches in {domain.upper()} ===")
        try:
            results = get_similar_documents(domain, query_text, top_k=3)
            memory_log["results"][domain] = []

            for score, obj in results:
                title = getattr(obj, "title", getattr(obj, "name", str(obj)))
                content = getattr(obj, "content", "")[:120]
                preview = content.replace("\n", " ")

                # Generate tags for each result (strings)
                tag_names = [t.lower().strip() for t in generate_tags_for_memory(content)]

                print(f"- {title} ({score:.4f}): {preview}... [Tags: {', '.join(tag_names)}]")

                # Log for memory metadata
                memory_log["results"][domain].append({
                    "title": title,
                    "score": round(score, 4),
                    "tags": tag_names,
                })

        except Exception as e:
            print(f"❌ Error searching {domain}: {e}")
        print()

    # Save a memory entry
    try:
        from memory.models import MemoryEntry

        summary = f"Vector search: {query_text[:50]}..."

        entry = MemoryEntry.objects.create(
            event=query_text,
            summary=summary,
            type="vector_search",
            source_role="system",  # or "assistant" if you'd rather attribute it
            is_conversation=False,
        )

        print(f"✅ MemoryEntry logged: {entry.id}")

    except Exception as e:
        print(f"❌ Failed to log MemoryEntry: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        custom_query = " ".join(sys.argv[1:])
        test_vector_query(custom_query)
    else:
        test_vector_query()
