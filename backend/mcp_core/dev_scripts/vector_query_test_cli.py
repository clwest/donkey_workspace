import sys
import os

# Setup Django
import django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from embeddings.helpers.helpers_similarity import get_similar_documents

def test_vector_query(query_text="How does the assistant handle memory reflection?"):
    print(f"🔍 Query: {query_text}\n")

    domains = ["prompt", "assistantthoughtlog", "devdoc"]
    for domain in domains:
        print(f"=== Top Matches in {domain.upper()} ===")
        try:
            results = get_similar_documents(domain, query_text, top_k=3)
            for score, obj in results:
                title = getattr(obj, 'title', getattr(obj, 'name', str(obj)))
                preview = getattr(obj, 'content', '')[:120].replace("\n", " ")
                print(f"- {title} ({score:.4f}): {preview}...")
        except Exception as e:
            print(f"❌ Error searching {domain}: {e}")
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        custom_query = " ".join(sys.argv[1:])
        test_vector_query(custom_query)
    else:
        test_vector_query()