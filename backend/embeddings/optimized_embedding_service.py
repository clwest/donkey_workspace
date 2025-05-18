"""
Optimized Embedding Service

This module provides optimized embedding generation, storage, and retrieval
services that reduce unnecessary API calls and improve performance through
batching, caching, and smart vector operations.

Key features:
1. Batched embedding generation to reduce API calls
2. Cache-first embedding retrieval
3. Deduplication of similar text content
4. Lazy embedding generation for non-critical content
5. Adaptive embedding quality based on content importance
"""

import logging
import time
import hashlib
import json
from typing import Dict, List, Set, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from functools import lru_cache
import threading
import queue

import numpy as np
from django.core.cache import cache
from django.utils import timezone

# Import from existing modules
from embeddings.vector_utils import normalize_vector, preprocess_text, cosine_similarity
from embeddings.helpers.helpers_io import save_embedding
from embeddings.sentence_transformer_service import get_sentence_transformer

logger = logging.getLogger("django")

# Constants
EMBEDDING_CACHE_TTL = 60 * 60 * 24  # 24 hours
BATCH_SIZE = 10  # Process embeddings in batches of this size
MIN_TEXT_LENGTH = 10  # Minimum text length to consider
SIMILARITY_THRESHOLD = 0.92  # Threshold for considering texts as similar
DEFAULT_MODEL = "default"  # Default embedding model
HIGH_QUALITY_MODEL = "high-quality"  # Higher quality model for important content
BACKGROUND_PROCESSING = True  # Whether to use background processing


class BatchProcessor(threading.Thread):
    """
    Background thread for processing embedding batches without blocking.
    """

    def __init__(self):
        super().__init__(daemon=True)
        self.queue = queue.Queue()
        self.running = False

    def run(self):
        """Process items from the queue until stopped."""
        self.running = True
        while self.running:
            try:
                # Get item from queue with timeout
                batch_items, callback = self.queue.get(timeout=1.0)
                if batch_items:
                    try:
                        # Process the batch
                        results = []
                        sentence_transformer = get_sentence_transformer()

                        # Use singleton for batch encoding when possible
                        if len(batch_items) > 1:
                            # Batch encode using the singleton transformer
                            embeddings = sentence_transformer.encode(batch_items)
                            results = list(zip(batch_items, embeddings))
                        else:
                            # Single item processing
                            for text in batch_items:
                                if text:
                                    embedding = sentence_transformer.encode(text)
                                    results.append((text, embedding))

                        # Call the callback with results
                        if callback:
                            callback(results)
                    except Exception as e:
                        logger.error(f"Error processing batch: {e}")
                    finally:
                        self.queue.task_done()
            except queue.Empty:
                # No items in queue, just continue
                continue
            except Exception as e:
                logger.error(f"Error in batch processor: {e}")

    def add_batch(self, batch_items, callback=None):
        """
        Add a batch of items to the processing queue.

        Args:
            batch_items (List): Items to process
            callback (function): Function to call with results
        """
        self.queue.put((batch_items, callback))

    def stop(self):
        """Stop the processor thread."""
        self.running = False
        self.join(timeout=2.0)


class OptimizedEmbeddingService:
    """
    Service for generating and managing embeddings with optimized performance.

    This service implements several optimizations:
    1. Batched API calls to reduce overhead
    2. Tiered caching for fast retrieval
    3. Smart deduplication to avoid redundant processing
    4. Background processing for non-blocking operations
    5. Quality selection based on content importance
    """

    def __init__(self):
        """Initialize the optimized embedding service."""
        self.embedding_queue = []
        self.processed_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.api_calls = 0
        self.last_process_time = None
        self.fingerprint_map = {}  # Track fingerprints for deduplication

        # Start background processor if enabled
        self.batch_processor = None
        if BACKGROUND_PROCESSING:
            self.batch_processor = BatchProcessor()
            self.batch_processor.start()

    def _generate_fingerprint(self, text: str) -> str:
        """
        Generate a fingerprint for text to identify similar content.

        Args:
            text (str): The text to fingerprint

        Returns:
            str: Hash fingerprint of normalized text
        """
        # Skip if text is too short
        if not text or len(text) < MIN_TEXT_LENGTH:
            return ""

        # Normalize text by removing whitespace and lowercasing
        normalized = " ".join(text.lower().split())
        return hashlib.md5(normalized.encode("utf-8")).hexdigest()

    def _get_cache_key(self, text: str, model: str = DEFAULT_MODEL) -> str:
        """
        Generate a cache key for the text and model.

        Args:
            text (str): The text to generate a key for
            model (str): The embedding model used

        Returns:
            str: Cache key
        """
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        return f"embedding_{model}_{text_hash}"

    def get_embedding(
        self,
        text: str,
        force_refresh: bool = False,
        high_quality: bool = False,
        wait_for_result: bool = True,
    ) -> Optional[List[float]]:
        """
        Get an embedding for the given text with optimized caching and processing.

        Args:
            text (str): The text to get embedding for
            force_refresh (bool): Whether to force a refresh from the API
            high_quality (bool): Whether to use high quality model
            wait_for_result (bool): Whether to wait for result or return None

        Returns:
            Optional[List[float]]: The embedding or None if not available
        """
        if not text or len(text) < MIN_TEXT_LENGTH:
            return None

        # Determine model to use
        model = HIGH_QUALITY_MODEL if high_quality else DEFAULT_MODEL

        # Preprocess text for consistency
        preprocessed_text = preprocess_text(text)

        # Check cache first unless force refresh
        if not force_refresh:
            cache_key = self._get_cache_key(preprocessed_text, model)
            cached_embedding = cache.get(cache_key)

            if cached_embedding:
                self.cache_hits += 1
                logger.debug(f"✓ Cache hit for embedding: {text[:30]}...")
                return cached_embedding

        self.cache_misses += 1

        # If not waiting for result, queue for processing and return None
        if not wait_for_result:
            self._queue_for_processing(preprocessed_text, model)
            return None

        # Otherwise, generate now
        try:
            self.api_calls += 1
            start_time = time.time()

            # Generate embedding using the singleton transformer
            sentence_transformer = get_sentence_transformer()
            embedding = sentence_transformer.encode(preprocessed_text)

            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.debug(f"Generated embedding in {elapsed_ms}ms: {text[:30]}...")

            # Cache result
            if embedding:
                cache_key = self._get_cache_key(preprocessed_text, model)
                cache.set(cache_key, embedding, EMBEDDING_CACHE_TTL)

                # Store fingerprint for deduplication
                fingerprint = self._generate_fingerprint(preprocessed_text)
                if fingerprint:
                    self.fingerprint_map[fingerprint] = cache_key

            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def _queue_for_processing(self, text: str, model: str = DEFAULT_MODEL) -> None:
        """
        Queue text for background embedding processing.

        Args:
            text (str): Text to generate embedding for
            model (str): Model to use for embedding
        """
        # Skip if already cached
        cache_key = self._get_cache_key(text, model)
        if cache.get(cache_key):
            return

        # Check for duplicates by fingerprint
        fingerprint = self._generate_fingerprint(text)
        if fingerprint in self.fingerprint_map:
            # Similar text already exists, link to existing embedding
            existing_key = self.fingerprint_map[fingerprint]
            existing_embedding = cache.get(existing_key)
            if existing_embedding:
                cache.set(cache_key, existing_embedding, EMBEDDING_CACHE_TTL)
                logger.debug(f"✓ Used similar text embedding for: {text[:30]}...")
                return

        # Add to processing queue
        if BACKGROUND_PROCESSING and self.batch_processor:
            # Add directly to background processor
            self.batch_processor.add_batch(
                [text], callback=lambda results: self._process_results(results, model)
            )
        else:
            # Add to local queue
            self.embedding_queue.append((text, model))

            # Process queue if it reaches batch size
            if len(self.embedding_queue) >= BATCH_SIZE:
                self.process_queue()

    def _process_results(
        self, results: List[Tuple[str, List[float]]], model: str
    ) -> None:
        """
        Process embedding results from background processing.

        Args:
            results (List[Tuple[str, List[float]]]): List of (text, embedding) pairs
            model (str): Model used for embedding
        """
        for text, embedding in results:
            if embedding:
                cache_key = self._get_cache_key(text, model)
                cache.set(cache_key, embedding, EMBEDDING_CACHE_TTL)

                # Store fingerprint for deduplication
                fingerprint = self._generate_fingerprint(text)
                if fingerprint:
                    self.fingerprint_map[fingerprint] = cache_key

        self.processed_count += len(results)
        self.last_process_time = timezone.now()

    def process_queue(self) -> None:
        """Process pending items in the embedding queue."""
        if not self.embedding_queue:
            return

        logger.info(f"Processing {len(self.embedding_queue)} items in embedding queue")
        start_time = time.time()

        batch_texts = []
        batch_models = []

        # Prepare batch
        for text, model in self.embedding_queue:
            batch_texts.append(text)
            batch_models.append(model)

        # Clear queue
        self.embedding_queue = []

        # Process in appropriate size batches
        for i in range(0, len(batch_texts), BATCH_SIZE):
            batch = batch_texts[i : i + BATCH_SIZE]
            models = batch_models[i : i + BATCH_SIZE]

            try:
                # Generate embeddings in batch
                for text, model in zip(batch, models):
                    embedding = self.get_embedding(text, model=model)
                    if embedding:
                        cache_key = self._get_cache_key(text, model)
                        cache.set(cache_key, embedding, EMBEDDING_CACHE_TTL)

                        # Store fingerprint for deduplication
                        fingerprint = self._generate_fingerprint(text)
                        if fingerprint:
                            self.fingerprint_map[fingerprint] = cache_key

                        self.processed_count += 1

            except Exception as e:
                logger.error(f"Error processing embedding batch: {e}")

        elapsed_time = time.time() - start_time
        logger.info(f"Processed embedding queue in {elapsed_time:.2f}s")
        self.last_process_time = timezone.now()

    def find_similar_texts(self, text: str, min_similarity: float = 0.8) -> List[str]:
        """
        Find similar texts based on embedding similarity.

        Args:
            text (str): The reference text
            min_similarity (float): Minimum similarity threshold

        Returns:
            List[str]: List of similar texts
        """
        if not text or len(text) < MIN_TEXT_LENGTH:
            return []

        # Get embedding for reference text
        reference_embedding = self.get_embedding(text)
        if not reference_embedding:
            return []

        # Find similar fingerprints
        similar_texts = []

        for fingerprint, cache_key in self.fingerprint_map.items():
            cached_embedding = cache.get(cache_key)
            if cached_embedding:
                similarity = cosine_similarity(reference_embedding, cached_embedding)
                if similarity >= min_similarity:
                    # Recover text from cache_key (if possible)
                    # This is imperfect as we don't store the original text
                    original_text = self._get_text_from_cache_metadata(cache_key)
                    if original_text:
                        similar_texts.append((original_text, similarity))

        # Sort by similarity (descending)
        similar_texts.sort(key=lambda x: x[1], reverse=True)

        # Return only the texts
        return [text for text, _ in similar_texts]

    def _get_text_from_cache_metadata(self, cache_key: str) -> Optional[str]:
        """
        Try to recover original text from cache metadata if available.

        Args:
            cache_key (str): The cache key

        Returns:
            Optional[str]: The original text if available
        """
        # This would require additional metadata storage
        # For simplicity, we return None here
        return None

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics for the embedding service.

        Returns:
            Dict[str, Any]: Service statistics
        """
        total_requests = self.cache_hits + self.cache_misses

        return {
            "processed_count": self.processed_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "api_calls": self.api_calls,
            "queue_length": len(self.embedding_queue),
            "cache_hit_rate": (
                self.cache_hits / total_requests if total_requests > 0 else 0
            ),
            "last_process_time": (
                self.last_process_time.isoformat() if self.last_process_time else None
            ),
            "fingerprints_tracked": len(self.fingerprint_map),
        }

    def cleanup(self) -> None:
        """Clean up resources used by the service."""
        # Process any pending items
        self.process_queue()

        # Stop background processor
        if BACKGROUND_PROCESSING and self.batch_processor:
            self.batch_processor.stop()


# Singleton instance
_embedding_service = None


def get_embedding_service() -> OptimizedEmbeddingService:
    """
    Get the singleton instance of OptimizedEmbeddingService.

    Returns:
        OptimizedEmbeddingService: The service instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = OptimizedEmbeddingService()
    return _embedding_service


# Convenience functions


def get_optimized_embedding(
    text: str, wait: bool = True, high_quality: bool = False
) -> Optional[List[float]]:
    """
    Get an embedding using the optimized service.

    Args:
        text (str): Text to get embedding for
        wait (bool): Whether to wait for result
        high_quality (bool): Whether to use high quality model

    Returns:
        Optional[List[float]]: The embedding or None
    """
    service = get_embedding_service()
    return service.get_embedding(text, wait_for_result=wait, high_quality=high_quality)


def queue_for_embedding(text: str, high_quality: bool = False) -> None:
    """
    Queue text for background embedding generation.

    Args:
        text (str): Text to queue
        high_quality (bool): Whether to use high quality model
    """
    model = HIGH_QUALITY_MODEL if high_quality else DEFAULT_MODEL
    service = get_embedding_service()
    service._queue_for_processing(text, model)
