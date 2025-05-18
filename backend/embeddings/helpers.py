import logging
from openai import OpenAI
from dotenv import load_dotenv
from pgvector.django import L2Distance
from uuid import UUID
import hashlib
import uuid
from django.db import transaction
from django.db.models import F, Q
from functools import lru_cache
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
import time
import re
import json
from django.conf import settings
from django.core.cache import cache
import importlib
import asyncio
import threading
from .circuit_breaker import circuit_protected, CircuitOpenError
from utils.error_reporting import (
    ErrorTracker,
    error_handling_decorator,
    log_error,
    log_info,
    log_warning,
    add_tag,
    add_extra,
)

# Remove direct imports from vector_utils to avoid circular imports
from .sentence_transformer_service import get_sentence_transformer

load_dotenv()
client = OpenAI()
logger = logging.getLogger("django")

EMBEDDING_MODEL = getattr(
    settings, "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)
EMBEDDING_LENGTH = 1536
# Maximum number of retries for embedding generation
MAX_RETRIES = 3
# Default timeout for embedding generation (seconds)
EMBEDDING_TIMEOUT = 10


# Helper functions to lazily import vector_utils functions
def _get_preprocess_text():
    from .vector_utils import preprocess_text

    return preprocess_text


def _get_normalize_vector():
    from .vector_utils import normalize_vector

    return normalize_vector


def _get_cosine_similarity():
    from .vector_utils import vector_cosine_similarity

    return vector_cosine_similarity


def _get_vector_search():
    from .vector_utils import vector_search

    return vector_search




# Background thread pool for async processing
def run_async_task(func, *args, **kwargs):
    """Run a function in a background thread"""
    thread = threading.Thread(target=func, args=args, kwargs=kwargs)
    thread.daemon = True
    thread.start()
    return thread


# Fallback function for embedding generation when circuit is open
def _embedding_fallback(*args, **kwargs) -> Optional[np.ndarray]:
    """
    Fallback function when embedding generation circuit is open.

    This will log the failure and return None, which downstream
    code should handle gracefully.

    Returns:
        None: Always returns None
    """
    logger.error("🛑 Embedding service unavailable - circuit breaker is open")
    return None


# ---- Main Function to save chat messages with embeddings ---


@error_handling_decorator
def save_message(
    session, role: str, content: str, sentiment_score: Optional[float] = None
):
    """
    Save a chat message to the database and generate embeddings for user messages.

    This function handles the complete process of:
    1. Saves the message to the database
    2. Generates sentiment scores for the message if needed
    3. Generates and saves embeddings for user messages

    Args:
        session: The chat session
        role (str): The role of the message sender (e.g., "user", "assistant")
        content (str): The message content
        sentiment_score (float, optional): Pre-calculated sentiment score

    Returns:
        ChatMessage: The saved message object
    """
    from chatbots.models import ChatMessage

    # Add tags for error context
    add_tag("role", role)
    if hasattr(session, "session_id"):
        add_tag("session_id", str(session.session_id))

    with ErrorTracker(
        "Save Chat Message",
        {
            "role": role,
            "content_length": len(content) if content else 0,
            "has_sentiment": sentiment_score is not None,
        },
    ):
        try:
            # Validate inputs
            if session is None:
                log_error(
                    ValueError("Session is None"),
                    "Cannot save message: session is None",
                )
                return None

            if not content:
                log_warning("Received empty message content, saving minimal record")
                content = ""

            # Create and save the message
            message = ChatMessage.objects.create(
                session=session,
                role=role,
                content=content,
                sentiment_score=sentiment_score,
            )
            log_info(f"Saved {role} message", {"message_id": message.id})

            # Only generate embeddings for user messages (not assistant responses)
            # This saves storage space and processing time
            # Assistant responses can be retrieved from message history if needed
            if role.lower() == "user" and content:
                log_info(
                    f"Generating embedding for chat message", {"message_id": message.id}
                )

                # Generate & save embedding (only for user messages)
                text_for_embedding = content[
                    :8000
                ]  # Limit to 8000 chars for efficiency

                # Use the circuit-protected embedding generation
                embedding_vector = generate_embedding(text_for_embedding)

                if embedding_vector is not None:
                    # Use asynchronous embedding processing for non-critical operations
                    add_extra("embedding_status", "async_processing_started")

                    # Get session ID with robust fallback mechanisms
                    try:
                        if hasattr(session, "session_id"):
                            session_id_value = session.session_id
                        elif hasattr(session, "id"):
                            session_id_value = session.id
                        elif hasattr(session, "pk"):
                            session_id_value = session.pk
                        elif isinstance(session, dict) and "session_id" in session:
                            session_id_value = session["session_id"]
                        elif isinstance(session, str) or isinstance(session, uuid.UUID):
                            session_id_value = session
                        else:
                            # Last resort - get string representation
                            session_id_value = str(session)
                            log_warning(
                                f"Using string representation for session_id: {session_id_value}",
                                {"session_type": type(session).__name__},
                            )
                    except Exception as e:
                        log_error(e, "Error extracting session_id for embedding")
                        session_id_value = None

                    async_save_embedding(
                        content_type="chat_message",
                        content_id=message.id,
                        vector=embedding_vector,
                        session_id=session_id_value,
                    )
                else:
                    log_warning(
                        f"No embedding generated for message",
                        {"message_id": message.id},
                    )

            return message

        except Exception as e:
            log_error(e, f"Error saving message")
            return None


# ---- Centralized Function for Embedding Generation ----


@lru_cache(maxsize=1000)
def generate_embedding_cached(text: str) -> Optional[np.ndarray]:
    """
    Generate and cache embeddings for a text.

    This function caches results to avoid generating the same embedding multiple times.
    The cache is limited to the most recent 1000 unique inputs.

    Args:
        text (str): Text to generate embedding for

    Returns:
        numpy.ndarray: Generated embedding vector or None if failed
    """
    return generate_embedding(text, use_cache=False)


@error_handling_decorator
@circuit_protected(
    circuit_name="embedding-service",
    failure_threshold=5,
    reset_timeout=60.0,
    fallback=_embedding_fallback,
)
def generate_embedding(
    text: str,
    model: str = EMBEDDING_MODEL,
    use_cache: bool = True,
    preprocess: bool = True,
    timeout: int = EMBEDDING_TIMEOUT,
) -> Optional[np.ndarray]:
    """
    Generate embeddings for text using SentenceTransformer singleton.

    This function:
    1. Validates the input text
    2. Optionally preprocesses the text for better quality
    3. Optionally uses caching for performance
    4. Handles errors gracefully
    5. Resizes the embedding vector to match expected dimensions
    6. Uses circuit breaker pattern to prevent cascading failures

    IMPORTANT: When using the returned NumPy arrays in boolean contexts,
    always be explicit about how you want to evaluate the array:
    - Use .any() to check if any element meets a condition
    - Use .all() to check if all elements meet a condition
    - Never use a NumPy array directly in an if condition without .any() or .all()

    Examples:
        # CORRECT: Check if any elements are greater than 0
        if (embedding > 0).any():
            # do something

        # CORRECT: Check if all elements are less than 1
        if (embedding < 1).all():
            # do something

        # CORRECT: Check if embedding is not None before using
        if embedding is not None and (embedding > 0.5).any():
            # do something

        # INCORRECT: This will raise a ValueError
        if embedding:  # DON'T do this with NumPy arrays!
            # do something

    Args:
        text (str): Text to generate embedding for
        model (str): Embedding model name (kept for API compatibility)
        use_cache (bool): Whether to use caching
        preprocess (bool): Whether to apply text preprocessing
        timeout (int): Timeout in seconds for embedding generation

    Returns:
        numpy.ndarray: Generated embedding vector or None if failed

    Raises:
        ValueError: If the input text is not valid or if array operations fail
        TypeError: If the input has an unexpected type
        CircuitOpenError: If the circuit breaker is open
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())[:8]  # For tracking this specific request in logs

    # Add tags for error context
    add_tag("request_id", request_id)
    add_tag("model", model)
    add_tag("preprocess", str(preprocess))
    add_tag("use_cache", str(use_cache))

    with ErrorTracker(
        "Embedding Generation",
        {"text_length": len(text) if text else 0, "model": model},
    ):
        try:
            # 🔍 Enhanced validation: Ensure input is a string, not an embedding list
            if text is None:
                log_warning(
                    "Embedding skipped: Input text is None", {"request_id": request_id}
                )
                return None

            if not isinstance(text, str):
                log_warning(
                    "Embedding skipped: Invalid input type",
                    {"request_id": request_id, "type": type(text).__name__},
                )
                return None

            if not text.strip():
                log_warning("Embedding skipped: Empty text", {"request_id": request_id})
                return None

            if isinstance(
                text, list
            ):  # 🚨 If embedding list is mistakenly passed, log and prevent error
                log_error(
                    TypeError("Received list instead of text"),
                    "Embedding Error: Received list instead of text. Skipping.",
                    {"request_id": request_id},
                )
                return None

            # Use caching if enabled (for frequently reused texts)
            if use_cache and len(text) > 10:  # Only cache non-trivial texts
                # Generate a deterministic hash of the text for cache key
                text_hash = hashlib.md5(text.encode()).hexdigest()
                cached_result = get_cache(f"embedding_{text_hash}")
                if cached_result is not None:
                    log_info(
                        f"Using cached embedding",
                        {
                            "request_id": request_id,
                            "text_preview": (
                                text[:30] + "..." if len(text) > 30 else text
                            ),
                        },
                    )
                    return cached_result

            # Log start of embedding generation
            log_info(
                f"Starting embedding generation",
                {"request_id": request_id, "text_length": len(text)},
            )

            # Apply preprocessing if enabled
            if preprocess:
                processed_text = _get_preprocess_text()(text)
                # If preprocessing resulted in empty text, use original
                if not processed_text.strip():
                    processed_text = text.replace("\n", " ")

                add_extra(
                    "preprocessing",
                    {
                        "original_length": len(text),
                        "processed_length": len(processed_text),
                        "used_original": not processed_text.strip(),
                    },
                )
            else:
                processed_text = text.replace("\n", " ")

            # Add retry logic for more robust embedding generation
            retry_count = 0
            embedding = None
            last_error = None

            while retry_count < MAX_RETRIES and embedding is None:
                try:
                    # Get the singleton transformer and generate embedding with timeout
                    transformer = get_sentence_transformer()

                    # Check if we're out of time
                    elapsed = time.time() - start_time
                    if elapsed > timeout:
                        log_warning(
                            f"Embedding timeout",
                            {
                                "request_id": request_id,
                                "elapsed_time": f"{elapsed:.2f}s",
                                "timeout": timeout,
                            },
                        )
                        return None

                    # Generate the embedding
                    embedding = transformer.encode(processed_text)

                except Exception as e:
                    retry_count += 1
                    last_error = e
                    log_warning(
                        f"Embedding error on retry attempt",
                        {
                            "request_id": request_id,
                            "attempt": retry_count,
                            "max_retries": MAX_RETRIES,
                            "error": str(e),
                        },
                    )

                    # Add exponential backoff between retries
                    if retry_count < MAX_RETRIES:
                        backoff_time = min(2**retry_count * 0.1, 1.0)  # Max 1 second
                        time.sleep(backoff_time)

            # If we exhausted all retries and still failed, log and return None
            if embedding is None:
                log_error(
                    last_error or Exception("Unknown error"),
                    f"Failed to generate embedding after all retries",
                    {"request_id": request_id, "retries": MAX_RETRIES},
                )
                return None

            # Check embedding dimensions and resize if needed
            if embedding is not None:
                # Convert to numpy array if it's not already
                embedding_np = np.array(embedding)

                # Get the expected dimension from the model
                from .models import EMBEDDING_LENGTH

                expected_dim = EMBEDDING_LENGTH

                # Make sure embedding_np is not empty before checking its shape
                if embedding_np.size == 0:
                    log_error(
                        ValueError("Generated embedding is empty"),
                        "Generated embedding is empty (zero-size array)",
                        {"request_id": request_id},
                    )
                    return None

                actual_dim = embedding_np.shape[0]

                # If dimensions don't match, resize the embedding
                if actual_dim != expected_dim:
                    log_info(
                        f"Resizing embedding dimensions",
                        {
                            "request_id": request_id,
                            "from_dim": actual_dim,
                            "to_dim": expected_dim,
                        },
                    )

                    if actual_dim < expected_dim:
                        # If the embedding is smaller than expected, pad with zeros
                        padding = np.zeros(expected_dim - actual_dim)
                        embedding_np = np.concatenate([embedding_np, padding])
                    else:
                        # If the embedding is larger than expected, truncate
                        embedding_np = embedding_np[:expected_dim]

                    embedding = embedding_np

                # Normalize the embedding vector for consistency
                embedding = _get_normalize_vector()(embedding_np)

                # Cache the result if caching is enabled
                if use_cache and len(text) > 10:
                    text_hash = hashlib.md5(text.encode()).hexdigest()
                    set_cache(
                        f"embedding_{text_hash}", embedding, timeout=86400
                    )  # Cache for 24 hours

                # Log successful completion with timing
                elapsed = time.time() - start_time
                log_info(
                    f"Successfully generated embedding",
                    {
                        "request_id": request_id,
                        "elapsed_time": f"{elapsed:.2f}s",
                        "dimensions": (
                            embedding.shape[0]
                            if hasattr(embedding, "shape")
                            else len(embedding)
                        ),
                    },
                )

                return embedding
            else:
                log_error(
                    ValueError("Model returned None"),
                    "Failed to generate embedding: model returned None",
                    {"request_id": request_id},
                )
                return None

        except ValueError as ve:
            log_error(ve, f"NumPy array operation error", {"request_id": request_id})
            return None
        except TypeError as te:
            log_error(
                te, f"Type error in embedding generation", {"request_id": request_id}
            )
            return None
        except Exception as e:
            elapsed = time.time() - start_time
            log_error(
                e,
                f"Unhandled error in embedding generation",
                {"request_id": request_id, "elapsed_time": f"{elapsed:.2f}s"},
            )
            return None


def generate_unique_id(name: str, fiscal_year: str) -> UUID:
    """
    Generate a deterministic UUID from a name and fiscal year.

    This creates a consistent, unique identifier that can be reproduced
    given the same inputs, useful for cross-referencing related data.

    Args:
        name (str): Name or primary identifier
        fiscal_year (str): Fiscal year or secondary identifier

    Returns:
        UUID: A deterministic UUID
    """
    return uuid.UUID(hashlib.md5(f"{name}{fiscal_year}".encode()).hexdigest())


# ---- Save Embeddings Efficiently ----
def save_embedding(
    content_type: str,
    content_id: Any,
    vector: np.ndarray,
    session_id: Optional[UUID] = None,
    source_type: Optional[str] = None,
    topic_id: Optional[UUID] = None,
) -> Any:
    """
    Save an embedding to the centralized embedding table.

    This function handles the common task of saving embeddings with proper
    normalization and association with content, sessions, and topics.

    Args:
        content_type (str): Type of content (e.g., "document", "chat_message")
        content_id: ID of the content
        vector (numpy.ndarray): The embedding vector
        session_id (UUID, optional): ID of the session
        source_type (str, optional): Source type (e.g., "URL", "YouTube")
        topic_id (UUID, optional): ID of the associated topic

    Returns:
        Embedding: The saved embedding instance or None if failed
    """
    # Import models here to avoid circular imports
    from .models import Embedding
    from intel_core.models import Document
    from chatbots.models import Topic

    try:
        # Validate vector input
        if vector is None or not isinstance(vector, (list, np.ndarray)):
            logger.error(
                f"❌ Invalid vector type: {type(vector)}. Must be list or numpy.ndarray"
            )
            return None

        # Handle different ID types based on content_type
        if content_type == "chat_message":
            # For chat messages, keep the original ID (likely an integer)
            # Convert to string for storage in content_id field
            content_id_str = str(content_id)
        elif content_type == "document" and not isinstance(content_id, uuid.UUID):
            # For documents, ensure UUID format
            try:
                # Try to convert string to UUID if it's in UUID format
                content_id_str = str(uuid.UUID(str(content_id)))
            except (ValueError, TypeError):
                # If not a valid UUID, generate a consistent one
                content_id_str = str(generate_unique_id(str(content_id), "2024"))
        else:
            # Default case: convert to string
            content_id_str = str(content_id)

        logger.info(f"🚀 Saving embedding for {content_type} ID {content_id_str}...")

        # Normalize the vector before saving
        normalized_vector = _get_normalize_vector()(vector)

        embedding = Embedding.objects.create(
            content_type=content_type,
            content_id=content_id_str,
            embedding=normalized_vector,
            session_id=session_id,
            source_type=source_type,
            topic=Topic.objects.filter(id=topic_id).first() if topic_id else None,
        )

        return embedding
    except Exception as e:
        logger.error(f"❌ Error saving embedding: {str(e)}", exc_info=True)
        return None


def async_save_embedding(
    content_type: str,
    content_id: Any,
    vector: np.ndarray,
    session_id: Optional[UUID] = None,
    source_type: Optional[str] = None,
    topic_id: Optional[UUID] = None,
) -> None:
    """
    Asynchronously save an embedding to the centralized embedding table.

    This function runs the save_embedding function in a background thread,
    allowing the caller to continue without waiting for the database operation.

    Args:
        Same parameters as save_embedding

    Returns:
        None (operation runs in background)
    """
    logger.info(
        f"🚀 Starting async embedding save for {content_type} ID {content_id}..."
    )
    run_async_task(
        save_embedding,
        content_type=content_type,
        content_id=content_id,
        vector=vector,
        session_id=session_id,
        source_type=source_type,
        topic_id=topic_id,
    )
    return None


# ---- Retrieve Embeddings ----
def retrieve_embeddings(session_id: str) -> List[np.ndarray]:
    """
    Retrieve all embeddings for a given chat session.

    Args:
        session_id (str): ID of the session to retrieve embeddings for

    Returns:
        list: List of embedding vectors

    Raises:
        ValueError: If session_id is invalid
    """
    # Import models here to avoid circular imports
    from .models import Embedding

    try:
        uuid_session_id = UUID(session_id)
    except ValueError:
        raise ValueError("Invalid UUID format for session ID.")
    return list(
        Embedding.objects.filter(session_id=uuid_session_id).values_list(
            "embedding", flat=True
        )
    )


# ---- Find Similar Messages Using Embeddings ----
def search_similar_embeddings(
    query: Union[str, List[float], np.ndarray], session_id: str, top_n: int = 5
) -> List[Tuple[str, float]]:
    """
    Search for similar embeddings to the query in the database.

    Args:
        query (Union[str, List[float], np.ndarray]): Query text or embedding vector
        session_id (str): Session ID to search in
        top_n (int): Number of results to return

    Returns:
        List[Tuple[str, float]]: List of (document_id, similarity_score) tuples
    """
    # Track performance and generate a request ID for this search
    start_time = time.time()
    request_id = str(uuid.uuid4())[:8]

    # Early return if inputs are invalid
    if not query:
        logger.error(
            f"❌ [Req:{request_id}] Invalid empty query in search_similar_embeddings"
        )
        return []

    if not session_id:
        logger.error(
            f"❌ [Req:{request_id}] Invalid empty session_id in search_similar_embeddings"
        )
        return []

    # Check if input is embedding or text
    is_vector = isinstance(query, (list, np.ndarray))

    # Skip embedding generation if query is already an embedding
    if is_vector:
        # Check if it's a list or numpy array with the expected embedding dimension
        dimension_check = (
            len(query) == EMBEDDING_LENGTH
            if isinstance(query, list)
            else (
                query.shape[0] == EMBEDDING_LENGTH
                if isinstance(query, np.ndarray)
                else False
            )
        )

        if dimension_check:
            logger.debug(
                f"ℹ️ [Req:{request_id}] Skipping redundant embedding generation (query is already an embedding)"
            )
            query_embedding = query
        else:
            logger.warning(
                f"⚠️ [Req:{request_id}] Query appears to be a vector but has wrong dimensions: {len(query) if isinstance(query, list) else query.shape}"
            )
            return []
    else:
        # Generate embedding for text query
        if not isinstance(query, str):
            logger.error(
                f"❌ [Req:{request_id}] Query must be a string, list, or numpy array. Got {type(query)}"
            )
            return []

        logger.debug(
            f"🔍 [Req:{request_id}] Generating embedding for query: {query[:100]}..."
        )
        query_embedding = generate_embedding(query)

    if query_embedding is None:
        logger.error(f"❌ [Req:{request_id}] Error: Query embedding generation failed!")
        return []

    try:
        # Use the optimized vector_search function
        logger.debug(
            f"🔍 [Req:{request_id}] Performing vector search with session_id={session_id}"
        )
        results = _get_vector_search()(
            query_embedding=query_embedding, session_id=session_id, limit=top_n
        )

        # Import here to avoid circular imports
        from .fine_tune import filter_similar_results

        # Convert to the format expected by existing code
        similarity_results = [
            (result["id"], result["similarity"]) for result in results
        ]

        # Log performance metrics
        elapsed = time.time() - start_time
        result_count = len(similarity_results)
        logger.info(
            f"✅ [Req:{request_id}] Found {result_count} similar embeddings in {elapsed:.2f}s"
        )

        return filter_similar_results(similarity_results)
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(
            f"❌ [Req:{request_id}] Error in search_similar_embeddings after {elapsed:.2f}s: {str(e)}",
            exc_info=True,
        )
        return []


# ---- Update Memory Efficiently ----
def update_memory(user, memory_key: str, memory_value: str) -> None:
    """
    Update chatbot memory with efficient embedding generation.

    This function creates or updates a ChatMemory entry with
    the preprocessed embedding of the memory value.

    Args:
        user (User): The user to update memory for
        memory_key (str): Key for the memory entry
        memory_value (str): Value to store in memory
    """
    # from chatbots.models import ChatMemory
    from django.core.cache import cache

    try:
        if not isinstance(memory_value, str):
            logger.warning(
                f"⚠️ Warning: memory_value is not a string (type: {type(memory_value)}). Skipping embedding."
            )
            return

        # Check cache first
        cache_key = f"memory_embedding_{user.id}_{memory_key}"
        cached_embedding = cache.get(cache_key)

        if cached_embedding:
            logger.info(f"✅ Using cached embedding for {memory_key}")
            memory, _ = ChatMemory.objects.get_or_create(
                user=user, memory_key=memory_key
            )
            memory.memory_value = memory_value
            memory.message_embedding = cached_embedding
            memory.save()
            return

        # Generate embedding with preprocessing
        embedding = generate_embedding(memory_value, preprocess=True)

        # Cache the embedding
        # cache.set(cache_key, embedding, timeout=3600)  # Cache for 1 hour

        # # Update or create memory entry
        # memory, _ = ChatMemory.objects.get_or_create(user=user, memory_key=memory_key)
        # memory.memory_value = memory_value
        # memory.message_embedding = embedding
        # memory.save()

        logger.info(f"✅ Updated memory and embedding for {memory_key}")

    except Exception as e:
        logger.error(f"❌ Error updating memory: {str(e)}", exc_info=True)


# ------ Force Retrieval of top 5 similar messages -----


def retrieve_similar_messages(user_message: str, user, top_n: int = 5) -> List[str]:
    """
    Retrieve the most similar past messages from chat history.

    Args:
        user_message (str): The message to find similar messages for
        user (User): The user to retrieve messages for
        top_n (int): Maximum number of messages to return

    Returns:
        list: List of message contents
    """
    # # Import here to avoid circular imports
    # from chatbots.models import ChatSession, ChatMessage

    # try:
    #     # ✅ Retrieve all sessions associated with the user
    #     user_sessions = ChatSession.objects.filter(user=user)

    #     # ✅ Ensure we query messages from those sessions
    #     chat_messages = ChatMessage.objects.filter(session__in=user_sessions).order_by("-created_at")[:top_n]

    #     retrieved_messages = [msg.content for msg in chat_messages]

    #     return retrieved_messages
    # except Exception as e:
    #     logger.error(f"❌ Error retrieving similar messages: {str(e)}", exc_info=True)
    #     return []


# ---- Helper functions for cache access ----


def get_cache(key: str) -> Any:
    """
    Get a value from the cache.

    Args:
        key (str): Cache key

    Returns:
        any: Cached value or None if not found
    """
    try:
        return cache.get(key)
    except Exception as e:
        logger.error(f"❌ Error getting cache: {str(e)}", exc_info=True)
        return None


def set_cache(key: str, value: Any, timeout: int = 3600) -> None:
    """
    Set a value in the cache.

    Args:
        key (str): Cache key
        value (any): Value to cache
        timeout (int): Cache timeout in seconds (default: 1 hour)
    """
    try:
        cache.set(key, value, timeout)
    except Exception as e:
        logger.error(f"❌ Error setting cache: {str(e)}", exc_info=True)
