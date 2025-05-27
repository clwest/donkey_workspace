"""
Vector Search Utilities
======================

This module provides optimized utilities for vector operations and similarity search.
It centralizes vector operations to ensure consistency and performance across the application.

Key Features:
- Standardized vector normalization
- Efficient similarity calculations
- Vector preprocessing functions
- Optimized database vector search operations

IMPORTANT: When working with NumPy arrays, always use .any() or .all() when evaluating
them in boolean contexts to avoid the "truth value of an array is ambiguous" error.

Usage:
```python
from embeddings.vector_utils import normalize_vector, cosine_similarity, vector_search

# Normalize a vector
normalized_vec = normalize_vector(my_vector)

# Calculate similarity
similarity = cosine_similarity(vec1, vec2)

# Search for similar vectors in database
results = vector_search(query_embedding, "document", limit=5, min_similarity=0.7)
```
"""

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    np = None
import logging
from typing import List, Dict, Any, Union, Optional, Tuple
from django.db.models import Q
from pgvector.django import CosineDistance
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from embeddings.helpers.nltk_data_loader import ensure_nltk_data
from uuid import UUID
from django.db import connection
from utils.cache_utils import VectorCache
from django.conf import settings

# Configure logger
logger = logging.getLogger("django")

# Initialize NLTK resources
ensure_nltk_data("punkt")
ensure_nltk_data("stopwords")

# Initialize stemmer
stemmer = PorterStemmer()
stop_words = set(stopwords.words("english"))


def preprocess_text(text: str) -> str:
    """
    Preprocess text for embedding generation.

    This function normalizes text by:
    1. Converting to lowercase
    2. Removing special characters
    3. Removing stop words
    4. Stemming words

    Args:
        text (str): The text to preprocess

    Returns:
        str: Preprocessed text
    """
    if not text or not isinstance(text, str):
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove special characters
    text = re.sub(r"[^\w\s]", " ", text)

    # Tokenize
    tokens = word_tokenize(text)

    # Remove stop words and apply stemming
    filtered_tokens = [stemmer.stem(word) for word in tokens if word not in stop_words]

    # Join tokens back into string
    return " ".join(filtered_tokens)


def normalize_vector(vec: Union[List[float], np.ndarray]) -> np.ndarray:
    """
    Normalize a vector to have unit length (L2 norm = 1).
    Ensures compatibility with NumPy arrays, PGVector, or list inputs.

    Args:
        vec (Union[List[float], np.ndarray]): The vector to normalize

    Returns:
        np.ndarray: The normalized vector as a numpy array with correct dimensions
    """
    if vec is None:
        raise ValueError("Cannot normalize None vector")

    if np is None:
        # Fallback: return vector unchanged as list
        return vec if isinstance(vec, list) else list(vec)

    try:
        # Convert to numpy array if needed
        if isinstance(vec, list):
            vec_np = np.array(vec, dtype=np.float32)
        elif isinstance(vec, np.ndarray):
            vec_np = vec.astype(np.float32)
        else:
            raise TypeError(f"Expected list or numpy array, got {type(vec)}")

        if vec_np.size == 0:
            raise ValueError("Cannot normalize empty vector")

        if np.isnan(vec_np).any():
            logger.warning("NaN values detected in vector - replacing with zeros")
            vec_np = np.nan_to_num(vec_np, nan=0.0)

        from embeddings.models import EMBEDDING_LENGTH
        if vec_np.shape[0] != EMBEDDING_LENGTH:
            if vec_np.shape[0] < EMBEDDING_LENGTH:
                padding = np.zeros(EMBEDDING_LENGTH - vec_np.shape[0], dtype=np.float32)
                vec_np = np.concatenate([vec_np, padding])
            else:
                vec_np = vec_np[:EMBEDDING_LENGTH]

        norm = np.linalg.norm(vec_np)
        if np.isclose(norm, 0):
            logger.warning("Vector with zero norm detected - returning zero vector")
            return np.zeros_like(vec_np)

        normalized = vec_np / norm

        if not np.all(np.isfinite(normalized)):
            logger.warning("Non-finite values in normalized vector - cleaning up")
            normalized = np.nan_to_num(normalized, nan=0.0, posinf=1.0, neginf=-1.0)

        normalized.flags.writeable = False  # Prevent accidental mutation
        return normalized

    except Exception as e:
        logger.error(f"Error normalizing vector: {str(e)}", exc_info=True)
        raise ValueError(f"Vector normalization failed: {str(e)}")


def cosine_similarity(
    vec1: Union[List[float], np.ndarray], vec2: Union[List[float], np.ndarray]
) -> float:
    """
    Calculate cosine similarity between two vectors.

    Cosine similarity measures the cosine of the angle between two vectors,
    ranging from -1 (opposite directions) to 1 (same direction).

    Args:
        vec1 (Union[List[float], np.ndarray]): First vector
        vec2 (Union[List[float], np.ndarray]): Second vector

    Returns:
        float: Similarity score between -1 and 1

    Raises:
        ValueError: If either vector is None or cannot be processed
    """
    if vec1 is None or vec2 is None:
        raise ValueError("Cannot compute similarity with None vectors")

    try:
        # Normalize vectors (ensures consistent results)
        vec1_norm = normalize_vector(vec1)
        vec2_norm = normalize_vector(vec2)

        if np is None:
            # Manual dot product fallback
            dot = sum(a * b for a, b in zip(vec1_norm, vec2_norm))
            norm1 = sum(a * a for a in vec1_norm) ** 0.5
            norm2 = sum(b * b for b in vec2_norm) ** 0.5
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return float(dot / (norm1 * norm2))

        # Calculate dot product of normalized vectors
        # (for normalized vectors, this equals cosine similarity)
        return float(np.dot(vec1_norm, vec2_norm))
    except Exception as e:
        logger.error(f"Error calculating cosine similarity: {str(e)}", exc_info=True)
        return 0.0


def compute_similarity(
    vec1: Union[List[float], np.ndarray],
    vec2: Union[List[float], np.ndarray],
) -> float:
    """Return cosine similarity clamped to the range 0..1."""
    try:
        raw = cosine_similarity(vec1, vec2)
        return max(0.0, min(1.0, raw))
    except Exception as e:
        logger.error(f"Error computing similarity: {e}", exc_info=True)
        return 0.0


def vector_search(
    query_embedding: Union[List[float], np.ndarray],
    content_type: Optional[str] = None,
    session_id: Optional[Union[str, UUID]] = None,
    topic_id: Optional[Union[str, UUID]] = None,
    limit: int = 5,
    min_similarity: float = 0.65,
) -> List[Dict[str, Any]]:
    """
    Perform optimized vector similarity search using database-level operations.

    This function uses PostgreSQL's vector operations via pgvector to perform
    efficient similarity search without loading all embeddings into memory.

    IMPORTANT: When working with the query_embedding parameter:
    - If it's a NumPy array, never use it directly in a boolean context
    - Always use .any() or .all() methods when evaluating array conditions
    - Always check if query_embedding is None before operations
    - Use isinstance() to check types before operations

    Examples:
        # CORRECT: Check for None and then verify array properties
        if query_embedding is not None and isinstance(query_embedding, np.ndarray):
            if (query_embedding > 0.5).any():
                # Do something

        # INCORRECT: Using array in boolean context
        if query_embedding:  # This will raise ValueError with numpy arrays
            # Do something

    Args:
        query_embedding (Union[List[float], np.ndarray]): The query embedding vector
        content_type (str, optional): Filter by content type (e.g., "document", "chat_message")
        session_id (str, optional): Filter by session ID
        topic_id (str, optional): Filter by topic ID
        limit (int): Maximum number of results to return
        min_similarity (float): Minimum similarity threshold (0-1)

    Returns:
        List[Dict[str, Any]]: List of matching results with similarity scores

    Raises:
        ValueError: If query_embedding is None or invalid
        TypeError: If query_embedding is of incorrect type
    """
    from embeddings.models import Embedding

    if query_embedding is None:
        raise ValueError("Query embedding cannot be None")

    try:
        # Convert list to numpy array if needed
        if isinstance(query_embedding, list):
            query_embedding = np.array(query_embedding, dtype=np.float32)

        # Validate that query_embedding is a numpy array
        if not isinstance(query_embedding, np.ndarray):
            raise TypeError(
                f"Query embedding must be a numpy array or list, got {type(query_embedding)}"
            )

        # Check if query_embedding is a NumPy array with valid dimensions
        from embeddings.models import EMBEDDING_LENGTH

        if query_embedding.size == 0:
            raise ValueError("Query embedding cannot be empty")

        if query_embedding.shape[0] != EMBEDDING_LENGTH:
            logger.warning(
                f"Query embedding has incorrect dimensions: {query_embedding.shape[0]}, expected {EMBEDDING_LENGTH}"
            )

            # Resize the embedding to match expected dimensions
            if query_embedding.shape[0] < EMBEDDING_LENGTH:
                # Pad with zeros
                padding = np.zeros(EMBEDDING_LENGTH - query_embedding.shape[0])
                query_embedding = np.concatenate([query_embedding, padding])
            else:
                # Truncate
                query_embedding = query_embedding[:EMBEDDING_LENGTH]

        # Normalize the query embedding
        normalized_query = normalize_vector(query_embedding)

        # Start building the query
        query = Embedding.objects.all()

        # Apply content_type filter if provided
        if content_type:
            query = query.filter(content_type=content_type)

        # Apply session_id filter if provided
        if session_id:
            query = query.filter(session_id=session_id)

        # Apply topic_id filter if provided
        if topic_id:
            query = query.filter(topic_id=topic_id)

        # Calculate cosine distance and filter by minimum similarity
        # Note: cosine distance = 1 - cosine similarity
        # So distance <= (1 - min_similarity) is equivalent to similarity >= min_similarity
        max_distance = 1 - min_similarity

        # Use pgvector's CosineDistance for efficient search at the database level
        results = (
            query.annotate(distance=CosineDistance("embedding", normalized_query))
            .filter(distance__lte=max_distance)
            .order_by("distance")
            .values("id", "content_type", "content_id", "distance", "topic_id")[:limit]
        )

        # Convert distance to similarity and format results
        formatted_results = []
        for result in results:
            # Convert distance to similarity (similarity = 1 - distance)
            similarity = 1 - result["distance"]

            formatted_results.append(
                {
                    "id": result["id"],
                    "content_type": result["content_type"],
                    "content_id": result["content_id"],
                    "similarity": similarity,
                    "topic_id": result["topic_id"],
                }
            )

        return formatted_results

    except ValueError as ve:
        logger.error(f"Vector search value error: {str(ve)}", exc_info=True)
        return []
    except TypeError as te:
        logger.error(f"Vector search type error: {str(te)}", exc_info=True)
        return []
    except Exception as e:
        logger.error(f"Vector search error: {str(e)}", exc_info=True)
        return []


def retrieve_content_for_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Retrieve actual content for vector search results, handling different ID types.

    This function takes the results from vector_search and adds the actual content
    from the database, properly handling the different types of IDs (int for chat messages,
    UUID for documents, etc.)

    Args:
        results (List[Dict[str, Any]]): Results from vector_search

    Returns:
        List[Dict[str, Any]]: Enhanced results with content added
    """
    import logging
    from chatbots.models import ChatMessage
    from intel_core.models import Document
    import uuid

    logger = logging.getLogger(__name__)
    enhanced_results = []

    for result in results:
        content_type = result.get("content_type")
        content_id = result.get("content_id")

        if not content_type or not content_id:
            # Skip incomplete results
            continue

        try:
            # Handle different content types
            if content_type == "chat_message":
                try:
                    # For chat messages, try as integer first
                    if isinstance(content_id, str) and content_id.isdigit():
                        content_id = int(content_id)
                    chat_message = ChatMessage.objects.filter(id=content_id).first()
                    if chat_message:
                        result["content"] = chat_message.content
                        result["created_at"] = chat_message.created_at
                except Exception as e:
                    logger.error(
                        f"Error retrieving chat message {content_id}: {str(e)}"
                    )

            elif content_type == "document":
                try:
                    # For documents, try as UUID first
                    if isinstance(content_id, str):
                        try:
                            # Try to convert to UUID if it looks like one
                            if len(content_id) == 36:  # Standard UUID length
                                content_id = uuid.UUID(content_id)
                        except (ValueError, TypeError):
                            # If not a valid UUID, just use as is
                            pass

                    document = Document.objects.filter(id=content_id).first()
                    if document:
                        result["content"] = document.content or document.title
                        result["title"] = document.title
                        result["metadata"] = document.metadata
                        result["created_at"] = document.created_at
                except Exception as e:
                    logger.error(f"Error retrieving document {content_id}: {str(e)}")

            # Add the result to our enhanced list
            enhanced_results.append(result)

        except Exception as e:
            logger.error(f"Error processing result {result}: {str(e)}")
            # Still add the result to avoid losing information
            enhanced_results.append(result)

    return enhanced_results


def enhanced_vector_search(
    query_embedding,
    content_type=None,
    session_id=None,
    topic_id=None,
    limit=5,
    min_similarity=0.7,
    recency_boost=0.2,
    reliability_boost=0.2,
    diversity_factor=0.3,
    source_reliability_weights=None,
    user_engagement_data=None,
):
    """
    Enhanced vector search with multi-factor ranking for improved retrieval quality.

    This function extends basic vector search by incorporating multiple ranking factors:
    - Vector similarity (semantic relevance)
    - Recency (newer documents get a boost)
    - Source reliability (trusted sources get a boost)
    - Diversity (using Maximum Marginal Relevance)

    Args:
        query_embedding (List[float]): The query embedding vector
        content_type (str, optional): Filter by content type (e.g., "document", "chat_message")
        session_id (str, optional): Filter by session ID
        topic_id (str, optional): Filter by topic ID
        limit (int): Maximum number of results to return
        min_similarity (float): Minimum similarity threshold (0-1)
        recency_boost (float): Weight for recency factor (0-1)
        reliability_boost (float): Weight for source reliability (0-1)
        diversity_factor (float): Weight for diversity in MMR (0-1, higher = more diverse)
        source_reliability_weights (dict, optional): Custom weights for different source types
        user_engagement_data (dict, optional): User engagement metrics for content

    Returns:
        List[Dict[str, Any]]: List of ranked results with similarity scores and metadata
    """
    from embeddings.models import Embedding
    from django.utils import timezone
    import math
    from datetime import timedelta
    from intel_core.models import Document

    logger.info(
        f"Running enhanced vector search with recency_boost={recency_boost}, reliability_boost={reliability_boost}"
    )

    # Default reliability weights if not provided
    if source_reliability_weights is None:
        source_reliability_weights = {
            "academic": 1.0,
            "technical": 1.0,
            "government": 0.95,
            "news": 0.85,
            "blog": 0.8,
            "social_media": 0.7,
            "forum": 0.75,
            "website": 0.8,
            "video": 0.85,
            "pdf": 0.9,
            "unknown": 0.7,
        }

    # Default engagement data structure if not provided
    if user_engagement_data is None:
        user_engagement_data = {}

    try:
        # Basic similarity search to get candidate results
        # We'll get more candidates than needed for re-ranking
        basic_results = vector_search(
            query_embedding=query_embedding,
            content_type=content_type,
            session_id=session_id,
            topic_id=topic_id,
            limit=limit * 3,  # Get more candidates for re-ranking
            min_similarity=min_similarity,
        )

        if not basic_results:
            logger.warning("No results found in basic vector search")
            return []

        # Current time for recency calculation
        now = timezone.now()

        # For testing, directly fetch document creation dates
        document_dates = {}
        if content_type == "document":
            doc_ids = [result.get("content_id") for result in basic_results]
            docs = Document.objects.filter(id__in=doc_ids)
            for doc in docs:
                document_dates[str(doc.id)] = doc.created_at

        # Apply multi-factor ranking
        enhanced_results = []
        for result in basic_results:
            # Start with base similarity score
            base_similarity = result.get("similarity", 0)

            # Get additional metadata for this result
            result_id = result.get("id")
            content_id = result.get("content_id")
            content_type_result = result.get("content_type")

            # Get document creation date directly if available
            if content_type == "document" and content_id in document_dates:
                created_at = document_dates[content_id]
            else:
                # Fallback to metadata lookup
                metadata = get_content_metadata(content_type_result, content_id)
                source_type = metadata.get("source_type", "unknown").lower()
                created_at = metadata.get(
                    "created_at", now - timedelta(days=30)
                )  # Default to 30 days old

            # 1. Recency factor (0-1, higher for newer content)
            age_in_days = (now - created_at).days if hasattr(created_at, "days") else 30

            # Apply exponential decay with stronger decay factor for better differentiation
            # Half-life of 7 days means content 7 days old gets a 0.5 recency score
            recency_factor = math.exp(-0.1 * max(0, age_in_days))

            # Log recency calculation for debugging
            logger.debug(
                f"Document age: {age_in_days} days, recency_factor: {recency_factor:.4f}"
            )

            # 2. Source reliability factor (0-1)
            # Find best matching source type
            reliability_factor = 0.7  # Default value
            if content_type == "document" and content_id in document_dates:
                # Get source type directly from document
                doc = Document.objects.get(id=content_id)
                source_type = doc.source_type.lower() if doc.source_type else "unknown"
                for source_key, weight in source_reliability_weights.items():
                    if source_key in source_type:
                        reliability_factor = weight
                        break
            else:
                # Fallback to metadata lookup
                metadata = get_content_metadata(content_type_result, content_id)
                source_type = metadata.get("source_type", "unknown").lower()
                for source_key, weight in source_reliability_weights.items():
                    if source_key in source_type:
                        reliability_factor = weight
                        break

            # 3. User engagement factor (if available)
            engagement_factor = 0.5  # Default value
            engagement_boost = 0.1  # Default weight for engagement
            if user_engagement_data and content_id in user_engagement_data:
                views = user_engagement_data.get(content_id, {}).get("views", 0)
                clicks = user_engagement_data.get(content_id, {}).get("clicks", 0)
                shares = user_engagement_data.get(content_id, {}).get("shares", 0)

                # Calculate engagement score (simple formula, can be refined)
                engagement_score = 0.5 + min(
                    0.5, (views * 0.01 + clicks * 0.05 + shares * 0.1)
                )
                engagement_factor = engagement_score

            # Ensure we have valid weights that sum to 1.0
            # Normalize weights if necessary
            total_boost = recency_boost + reliability_boost + engagement_boost
            if (
                total_boost > 0.9
            ):  # Cap total boosts at 90% to ensure similarity still matters
                scale_factor = 0.9 / total_boost
                recency_boost *= scale_factor
                reliability_boost *= scale_factor
                engagement_boost *= scale_factor
                total_boost = 0.9

            similarity_weight = 1.0 - total_boost

            # Calculate final score - properly weighted sum of all factors
            final_score = (
                base_similarity * similarity_weight
                + recency_factor * recency_boost
                + reliability_factor * reliability_boost
                + engagement_factor * engagement_boost
            )

            # Log detailed scoring for debugging
            logger.debug(
                f"Scoring - similarity: {base_similarity:.4f}*{similarity_weight:.2f}, "
                f"recency: {recency_factor:.4f}*{recency_boost:.2f}, "
                f"reliability: {reliability_factor:.4f}*{reliability_boost:.2f}, "
                f"engagement: {engagement_factor:.4f}*{engagement_boost:.2f}, "
                f"final: {final_score:.4f}"
            )

            # Store all factors and the final score
            enhanced_result = {
                **result,  # Include all original fields
                "recency_factor": recency_factor,
                "reliability_factor": reliability_factor,
                "engagement_factor": engagement_factor,
                "final_score": final_score,
                "source_type": source_type,
                "created_at": created_at,
                "age_in_days": age_in_days,
                # Add weights for debugging
                "similarity_weight": similarity_weight,
                "recency_boost": recency_boost,
                "reliability_boost": reliability_boost,
                "engagement_boost": engagement_boost,
            }

            enhanced_results.append(enhanced_result)

        # Sort by final score
        enhanced_results.sort(key=lambda x: x["final_score"], reverse=True)

        # Log top results to verify ranking is working
        if enhanced_results:
            logger.info(
                f"Top result - score: {enhanced_results[0]['final_score']:.4f}, age: {enhanced_results[0]['age_in_days']} days"
            )
            if len(enhanced_results) > 1:
                logger.info(
                    f"Second result - score: {enhanced_results[1]['final_score']:.4f}, age: {enhanced_results[1]['age_in_days']} days"
                )

        # Apply MMR for diversity if we have enough results and diversity is desired
        if len(enhanced_results) > 1 and diversity_factor > 0:
            final_results = apply_maximum_marginal_relevance(
                enhanced_results,
                query_embedding,
                lambda_param=1 - diversity_factor,  # Convert diversity to lambda
                limit=limit,
            )
        else:
            # Just take top results by score
            final_results = enhanced_results[:limit]

        logger.info(
            f"Enhanced search returned {len(final_results)} results from {len(enhanced_results)} candidates"
        )
        return final_results

    except Exception as e:
        logger.error(f"Error in enhanced vector search: {e}")
        return []


def apply_maximum_marginal_relevance(
    results, query_embedding, lambda_param=0.7, limit=5
):
    """
    Apply Maximum Marginal Relevance algorithm to rerank results for diversity.

    Args:
        results: List of search results with embeddings
        query_embedding: The original query embedding
        lambda_param: Trade-off between relevance (1) and diversity (0)
        limit: Number of results to return

    Returns:
        List of reranked results
    """
    # If we only have a few results, just return them
    if len(results) <= limit:
        return results

    from embeddings.models import Embedding
    if np is None:
        return results[:limit]

    # Initialize lists for selected and remaining results
    selected = []
    remaining = results.copy()

    # Add the most relevant document first
    selected.append(remaining.pop(0))

    # Iteratively add the next best document
    while len(selected) < limit and remaining:
        max_score = -1.0
        max_idx = -1

        for i, doc in enumerate(remaining):
            # Calculate relevance to query (already computed)
            relevance = doc["final_score"]

            # Calculate diversity (maximum similarity to any selected document)
            if not selected:
                diversity_penalty = 0
            else:
                # Get embedding for this document
                doc_id = doc["id"]
                embedding_obj = Embedding.objects.get(id=doc_id)
                doc_embedding = embedding_obj.embedding

                # Calculate similarities to all selected documents
                similarities = []
                for sel_doc in selected:
                    sel_id = sel_doc["id"]
                    sel_embedding_obj = Embedding.objects.get(id=sel_id)
                    sel_embedding = sel_embedding_obj.embedding

                    # Calculate cosine similarity
                    similarity = cosine_similarity(doc_embedding, sel_embedding)
                    similarities.append(similarity)

                # Use maximum similarity as diversity penalty
                diversity_penalty = max(similarities) if similarities else 0

            # Calculate MMR score
            mmr_score = (
                lambda_param * relevance - (1 - lambda_param) * diversity_penalty
            )

            # Update if this is the best score so far
            if mmr_score > max_score:
                max_score = mmr_score
                max_idx = i

        # Add the document with the highest MMR score
        if max_idx >= 0:
            selected.append(remaining.pop(max_idx))
        else:
            break

    return selected


def get_content_metadata(content_type, content_id):
    """
    Retrieve metadata for a content item based on its type and ID.

    Args:
        content_type (str): Type of content (e.g., "document", "chat_message")
        content_id (str): ID of the content

    Returns:
        dict: Metadata dictionary with source_type, created_at, etc.
    """
    from intel_core.models import Document
    from chatbots.models import ChatMessage

    metadata = {"source_type": "unknown"}

    try:
        if content_type == "document":
            # Retrieve document metadata
            document = Document.objects.filter(id=content_id).first()
            if document:
                metadata = {
                    "source_type": document.source_type,
                    "created_at": document.created_at,
                    "title": document.title,
                }

        elif content_type == "chat_message":
            # Retrieve chat message metadata
            message = ChatMessage.objects.filter(id=content_id).first()
            if message:
                metadata = {
                    "source_type": "chat_message",
                    "created_at": message.created_at,
                    "role": message.role,
                }

    except Exception as e:
        logger.error(f"Error retrieving metadata for {content_type} {content_id}: {e}")

    return metadata


class VectorSearchOptimizer:
    """Optimizes vector similarity searches using pgvector."""

    def __init__(self, table_name: str, vector_column: str = "embedding"):
        self.table_name = table_name
        self.vector_column = vector_column
        self._ensure_index()

    def _ensure_index(self) -> None:
        """Ensure vector index exists for efficient similarity search."""
        try:
            with connection.cursor() as cursor:
                # Check if index exists
                cursor.execute(
                    f"""
                    SELECT 1 FROM pg_class c
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE c.relname = '{self.table_name}_{self.vector_column}_idx'
                """
                )
                index_exists = cursor.fetchone() is not None

                if not index_exists:
                    # Create HNSW index for faster approximate search
                    cursor.execute(
                        f"""
                        CREATE INDEX {self.table_name}_{self.vector_column}_idx 
                        ON {self.table_name} 
                        USING hnsw ({self.vector_column} vector_cosine_ops)
                        WITH (m = 16, ef_construction = 64)
                    """
                    )
                    logger.info(
                        f"Created HNSW index for {self.table_name}.{self.vector_column}"
                    )
        except Exception as e:
            logger.error(f"Error ensuring vector index: {str(e)}")

    def find_similar(
        self,
        query_vector: np.ndarray,
        limit: int = 10,
        threshold: float = 0.7,
        filters: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Find similar vectors using optimized search.

        Args:
            query_vector: The query vector to find similarities for
            limit: Maximum number of results to return
            threshold: Minimum similarity threshold
            filters: Additional SQL WHERE conditions

        Returns:
            List of similar items with their similarity scores
        """
        # Try to get cached results first
        cached_results = VectorCache.get_cached_similarity(
            query_vector, self.table_name
        )
        if cached_results:
            return cached_results

        try:
            # Build optimized query
            query = f"""
                SELECT id, metadata, 
                       1 - ({self.vector_column} <=> %s::vector) as similarity
                FROM {self.table_name}
                WHERE 1 - ({self.vector_column} <=> %s::vector) > %s
            """

            # Add any additional filters
            if filters:
                for key, value in filters.items():
                    query += f" AND {key} = %s"

            query += f" ORDER BY similarity DESC LIMIT {limit}"

            # Execute query with parameters
            params = [query_vector.tolist(), query_vector.tolist(), threshold]
            if filters:
                params.extend(filters.values())

            with connection.cursor() as cursor:
                cursor.execute(query, params)
                results = []
                for row in cursor.fetchall():
                    results.append(
                        {"id": row[0], "metadata": row[1], "similarity": float(row[2])}
                    )

            # Cache results for future use
            VectorCache.cache_similarity_results(query_vector, self.table_name, results)

            return results

        except Exception as e:
            logger.error(f"Error in vector similarity search: {str(e)}")
            return []

    def batch_upsert_vectors(
        self,
        vectors: List[np.ndarray],
        metadata_list: List[Dict],
        chunk_size: int = 1000,
    ) -> None:
        """
        Efficiently upsert vectors in batches.

        Args:
            vectors: List of vectors to upsert
            metadata_list: List of metadata dictionaries
            chunk_size: Number of vectors to upsert in each batch
        """
        try:
            # Process in chunks for memory efficiency
            for i in range(0, len(vectors), chunk_size):
                chunk_vectors = vectors[i : i + chunk_size]
                chunk_metadata = metadata_list[i : i + chunk_size]

                # Build efficient upsert query
                query = f"""
                    INSERT INTO {self.table_name} (embedding, metadata)
                    VALUES %s
                    ON CONFLICT (id) DO UPDATE
                    SET embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata
                """

                # Prepare values for batch insert
                values = []
                for vec, meta in zip(chunk_vectors, chunk_metadata):
                    values.append((vec.tolist(), meta))

                with connection.cursor() as cursor:
                    cursor.execute(query, [values])

            logger.info(f"Successfully upserted {len(vectors)} vectors")

        except Exception as e:
            logger.error(f"Error in batch vector upsert: {str(e)}")

    def optimize_table(self) -> None:
        """Optimize the vector table for better performance."""
        try:
            with connection.cursor() as cursor:
                # Analyze table for query optimization
                cursor.execute(f"ANALYZE {self.table_name}")

                # Vacuum to reclaim space and update statistics
                cursor.execute(f"VACUUM ANALYZE {self.table_name}")

                logger.info(f"Successfully optimized table {self.table_name}")

        except Exception as e:
            logger.error(f"Error optimizing vector table: {str(e)}")


def create_vector_index(model) -> None:
    """Create vector index for a model's embedding field."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                CREATE INDEX IF NOT EXISTS {model._meta.db_table}_embedding_idx
                ON {model._meta.db_table}
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64)
            """
            )
    except Exception as e:
        logger.error(f"Error creating vector index: {str(e)}")


def optimize_vector_query(
    query_vector: np.ndarray, table_name: str, limit: int = 10, threshold: float = 0.7
) -> str:
    """Generate an optimized vector similarity query."""
    return f"""
        SELECT id, metadata,
               1 - (embedding <=> %s::vector) as similarity
        FROM {table_name}
        WHERE 1 - (embedding <=> %s::vector) > {threshold}
        ORDER BY similarity DESC
        LIMIT {limit}
    """
