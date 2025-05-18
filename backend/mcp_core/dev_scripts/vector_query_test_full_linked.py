import sys
import os
import django
import json
import uuid

# Django setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from embeddings.helpers.helpers_similarity import get_similar_documents
from embeddings.helpers.helper_tagging import generate_tags_for_memory
from memory.models import MemoryEntry
from mcp_core.models import Tag
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

def test_vector_query(query_text="How does the assistant handle memory reflection?"):
    print(f"🔍 Query: {query_text}\n")

    memory_log = {
        "query": query_text,
        "results": {}
    }

    collected_tags = set()
    top_result_obj = None
    domains = ["prompt", "assistantthoughtlog", "devdoc"]

    for domain in domains:
        print(f"=== Top Matches in {domain.upper()} ===")
        try:
            results = get_similar_documents(domain, query_text, top_k=3)
            memory_log["results"][domain] = []

            for idx, (score, obj) in enumerate(results):
                title = getattr(obj, 'title', getattr(obj, 'name', str(obj)))
                content = getattr(obj, 'content', '')[:120]
                preview = content.replace("\n", " ")

                # Generate tags for each result
                tags = generate_tags_for_memory(content)
                tag_names = [tag.name for tag in tags]
                collected_tags.update(tags)

                print(f"- {title} ({score:.4f}): {preview}... [Tags: {', '.join(tag_names)}]")

                if idx == 0 and top_result_obj is None:
                    top_result_obj = obj

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
        summary = f"Vector search: {query_text[:50]}..."
        entry = MemoryEntry.objects.create(
            event=query_text,
            summary=summary,
            type="vector_search",
            source_role="system",
            is_conversation=False,
        )

        # Add tags to MemoryEntry
        if collected_tags:
            entry.tags.set(collected_tags)

        # Link the top object if it has .uuid or .id
        if top_result_obj:
            content_type = ContentType.objects.get_for_model(top_result_obj)
            entry.linked_content_type = content_type
            entry.linked_object_id = getattr(top_result_obj, "uuid", getattr(top_result_obj, "id", None))
            entry.save()

        print(f"✅ MemoryEntry logged: {entry.id}")

    except Exception as e:
        print(f"❌ Failed to log MemoryEntry: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        custom_query = " ".join(sys.argv[1:])
        test_vector_query(custom_query)
    else:
        test_vector_query()