from typing import List, Tuple, Any
from embeddings.vector_utils import compute_similarity
from embeddings.helpers.search_registry import search_registry
from embeddings.helpers.helpers_processing import generate_embedding  # or wherever your function is

def get_similar_documents(domain: str, query_text: str, top_k: int = 5) -> List[Tuple[float, Any]]:
    if domain not in search_registry:
        raise ValueError(f"Unknown domain: {domain}")

    model_info = search_registry[domain]
    queryset = model_info["queryset"]()
    embedding_field = model_info["embedding_field"]

    query_vector = generate_embedding(query_text)
    if not query_vector:
        raise ValueError("Query embedding failed.")

    results = []
    for obj in queryset:
        obj_vector = getattr(obj, embedding_field, None)
        if obj_vector is not None:
            score = compute_similarity(query_vector, obj_vector)
            results.append((score, obj))

    results.sort(key=lambda x: x[0], reverse=True)
    return results[:top_k]