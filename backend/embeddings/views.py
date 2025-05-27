# embeddings/api_views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from embeddings.helpers.helpers_processing import find_similar_characters
from embeddings.helpers.helpers_processing import generate_embedding
from embeddings.document_services.chunking import (
    generate_chunks,
    generate_chunk_fingerprint,
)
from embeddings.helpers.helpers_io import search_similar_embeddings_for_model
from embeddings.helpers.helpers_io import retrieve_embeddings
from embeddings.document_services.document_caching import (
    track_session_usage,
    get_session_docs,
)

# Models we want to support in similarity search
from prompts.models import Prompt
from mcp_core.models import MemoryContext
from assistants.models.thoughts import AssistantThoughtLog
from embeddings.helpers.helpers_processing import generate_embedding
from embeddings.vector_utils import compute_similarity
from embeddings.helpers.helpers_similarity import get_similar_documents
from embeddings.helpers.search_registry import search_registry


@api_view(["POST"])
def embed_text(request):
    text = request.data.get("text")
    if not text:
        return Response({"error": "No text provided."}, status=400)

    embedding = generate_embedding(text)
    if not embedding:
        return Response({"error": "Failed to generate embedding."}, status=500)

    return Response({"embedding": embedding})


# === 1. Embed raw text and return vector ===
@api_view(["POST"])
@permission_classes([AllowAny])
def embed_text_api(request):
    text = request.data.get("text")
    if not text:
        return Response({"error": "Missing text field."}, status=400)

    try:
        vector = embed_text(text)
        return Response({"embedding": vector})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


# === 2. Chunk large text and return chunk list ===
@api_view(["POST"])
@permission_classes([AllowAny])
def chunk_text_api(request):
    text = request.data.get("text")
    if not text:
        return Response({"error": "Missing text field."}, status=400)

    chunks = generate_chunks(text)
    enriched_chunks = [
        {"text": chunk, "fingerprint": generate_chunk_fingerprint(chunk)}
        for chunk in chunks
    ]
    return Response({"chunks": enriched_chunks})


# === 3. Vector similarity search ===
@api_view(["POST"])
@permission_classes([AllowAny])
def search_similar_embeddings_api(request):
    content_type = request.data.get("content_type")
    content_ids = request.data.get("content_ids")
    if not content_type or not content_ids:
        return Response({"error": "Missing content_type or content_ids."}, status=400)

    try:
        embeddings = retrieve_embeddings(content_type, content_ids)
        results = [
            {
                "content_id": emb.content_id,
                "score": 1.0,  # Placeholder until actual similarity search is implemented
                "content": emb.content,
            }
            for emb in embeddings
        ]
        return Response({"results": results})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


# === 4. Get session documents ===
@api_view(["GET"])
@permission_classes([AllowAny])
def session_docs_api(request, session_id):
    try:
        doc_ids = get_session_docs(session_id)
        return Response({"session_id": session_id, "documents": doc_ids})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


# === 5. Track session usage ===
@api_view(["POST"])
@permission_classes([AllowAny])
def track_session_api(request):
    session_id = request.data.get("session_id")
    doc_id = request.data.get("doc_id")
    if not session_id or not doc_id:
        return Response({"error": "Missing session_id or doc_id."}, status=400)

    try:
        track_session_usage(session_id, doc_id)
        return Response({"message": "Session usage tracked."})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


# embeddings/api_views.py (append below previous endpoints)


@api_view(["POST"])
def search_similar_characters(request):
    """Return characters similar to the given text.

    **Parameters**
    - `text` (str): Query text used to generate an embedding.
    - `top_n` (int, optional): Number of results to return. Defaults to ``5``.

    **Returns**
    ``{"results": [{"id": int, "name": str, "score": float}, ...]}``
    """
    text = request.data.get("text")
    top_n = int(request.data.get("top_n", 5))

    if not text:
        return Response(
            {"error": "No text provided."}, status=status.HTTP_400_BAD_REQUEST
        )

    vector = generate_embedding(text)
    if vector is None or (
        hasattr(vector, "__len__") and len(vector) == 0
    ):
        return Response(
            {"error": "Failed to generate embedding."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    results = find_similar_characters(vector, top_k=top_n)
    return Response({"results": results})


MODEL_LOOKUP = {
    "prompt": {
        "model": Prompt,
        "content_field": "content",
        "vector_field": "embedding",
    },
    "memory": {
        "model": MemoryContext,
        "content_field": "content",
        "vector_field": "embedding",
    },
    "thought": {
        "model": AssistantThoughtLog,
        "content_field": "thought",
        "vector_field": "embedding",
    },
}


@api_view(["POST"])
@permission_classes([AllowAny])
def search_embeddings(request):

    text = request.data.get("text")
    model_type = request.data.get("model_type")
    target = request.data.get("target")
    top_k = int(request.data.get("top_k", 5))

    if not text:
        return Response(
            {"error": "Text is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    if target:
        config = search_registry.get(target)
        if not config:
            return Response(
                {"error": f"Invalid target type: {target}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        vector = generate_embedding(text)
        if vector is None or (
            hasattr(vector, "__len__") and len(vector) == 0
        ):
            return Response(
                {"error": "Failed to generate embedding for query."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        matches = []
        for obj in config["queryset"]():
            obj_text = getattr(obj, config["text_field"], None)
            if not obj_text:
                continue

            if config["embedding_field"]:
                stored_vec = getattr(obj, config["embedding_field"], None)
                if stored_vec is not None and len(stored_vec) > 0:
                    score = compute_similarity(vector, stored_vec)
                else:
                    continue
            else:
                obj_vec = generate_embedding(obj_text)
                if not obj_vec:
                    continue
                score = compute_similarity(vector, obj_vec)

            matches.append(
                {
                    "id": getattr(obj, config["id_field"]),
                    "text": obj_text,
                    "score": round(score, 4),
                }
            )

        matches = sorted(matches, key=lambda x: x["score"], reverse=True)[:top_k]
        return Response({"results": matches})

    lookup_key = model_type or "prompt"
    config = MODEL_LOOKUP.get(lookup_key)
    if not config:
        return Response(
            {"error": f"Invalid model_type: {lookup_key}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    vector = generate_embedding(text)
    if vector is None or (
        hasattr(vector, "__len__") and len(vector) == 0
    ):
        return Response({"error": "Failed to generate embedding."}, status=500)

    results = search_similar_embeddings_for_model(
        query_vector=vector,
        model_class=config["model"],
        vector_field_name=config["vector_field"],
        content_field_name=config["content_field"],
        top_k=top_k,
    )

    return Response({"results": results}, status=200)


@api_view(["GET"])
@permission_classes([AllowAny])
def list_search_targets(request):
    """Return available search target types.

    **Returns**
    ``{"results": [{"key": str, "label": str}, ...]}``
    """
    targets = [
        {"key": key, "label": cfg["label"]} for key, cfg in search_registry.items()
    ]

