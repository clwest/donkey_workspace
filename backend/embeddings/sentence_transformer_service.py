"""
SentenceTransformer Service with Projection Layer

This module provides a singleton implementation for loading and accessing
the SentenceTransformer model with a projection layer to match OpenAI's dimensions.
"""

import logging
from sentence_transformers import SentenceTransformer, models
import threading
import numpy as np
import torch
import os

logger = logging.getLogger("django")


class SentenceTransformerService:
    """
    Singleton service for the SentenceTransformer model with dimension projection.

    This service ensures that the SentenceTransformer model is loaded only once
    and reused across the application, improving performance and reducing memory usage.

    The service includes a projection layer to convert embeddings from the model's
    native dimensions to 1536 dimensions to match OpenAI embeddings.
    """

    _instance = None
    _lock = threading.Lock()
    _model = None
    _base_model_name = "BAAI/bge-large-en-v1.5"  # High-quality embedding model
    _output_dim = 1536  # Target dimension to match OpenAI embeddings
    _initialized = False

    def __new__(cls, model_name=None):
        """
        Create a singleton instance of the SentenceTransformerService.

        Args:
            model_name (str, optional): The name of the base SentenceTransformer model to load.
                                       If None, defaults to BGE-large model.

        Returns:
            SentenceTransformerService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                base_model = model_name or cls._base_model_name
                logger.info(
                    f"Creating SentenceTransformerService singleton with base model: {base_model} and projection to {cls._output_dim} dimensions"
                )
                cls._instance = super(SentenceTransformerService, cls).__new__(cls)
                cls._instance._base_model_name = base_model
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, model_name=None):
        """
        Initialize the SentenceTransformerService with projection layer if not already initialized.

        Args:
            model_name (str, optional): The name of the base SentenceTransformer model to load.
                                       If None, defaults to BGE-large model.
        """
        # Use a class-level lock to ensure thread safety during initialization
        with self.__class__._lock:
            # Only initialize once
            if not self.__class__._initialized:
                base_model = model_name or self._base_model_name
                logger.info(
                    f"Initializing SentenceTransformer with base model: {base_model} and projection to {self._output_dim} dimensions"
                )
                try:
                    # Create the model with projection layer to resize to 1536 dimensions
                    self._init_model_with_projection(base_model)
                    self.__class__._initialized = True
                    logger.info(
                        f"✅ SentenceTransformer model loaded with projection layer: {base_model} → {self._output_dim} dimensions"
                    )
                except Exception as e:
                    logger.error(
                        f"❌ Error loading SentenceTransformer model: {str(e)}"
                    )
                    self.__class__._initialized = False

    def _init_model_with_projection(self, base_model_name):
        """
        Initialize the model with a projection layer to match OpenAI dimensions.

        Args:
            base_model_name (str): The name of the base SentenceTransformer model to load
        """
        try:
            # Set environment variable to use MPS (Metal Performance Shaders) on Mac if available
            if torch.backends.mps.is_available():
                os.environ["TOKENIZERS_PARALLELISM"] = "false"

            # Load the base transformer model
            base_model = models.Transformer(base_model_name)

            # Add pooling layer to get sentence embeddings
            pooling = models.Pooling(base_model.get_word_embedding_dimension())

            # Get the embedding dimension from the model
            base_dimension = pooling.get_sentence_embedding_dimension()
            logger.info(
                f"Base model dimension: {base_dimension}, projecting to: {self._output_dim}"
            )

            # Add projection layer to resize to 1536 dimensions
            projection = models.Dense(
                in_features=base_dimension,
                out_features=self._output_dim,
                activation_function=torch.nn.Tanh(),  # Adding non-linearity for better projection
            )

            # Combine into a SentenceTransformer model
            self.__class__._model = SentenceTransformer(
                modules=[base_model, pooling, projection]
            )

            # Log model information
            logger.info(f"Model architecture: {self.__class__._model}")
        except Exception as e:
            logger.error(f"Error initializing model with projection: {str(e)}")
            raise

    @property
    def model(self):
        """
        Get the SentenceTransformer model.

        Returns:
            SentenceTransformer: The loaded model or None if initialization failed
        """
        return self.__class__._model

    def encode_text(self, text, **kwargs):
        """
        Encode a single text using the SentenceTransformer model.

        Args:
            text (str): The text to encode
            **kwargs: Additional arguments to pass to the model's encode method

        Returns:
            np.ndarray: The embedding with 1536 dimensions
        """
        return self.encode(text, **kwargs)

    def encode_texts(self, texts, **kwargs):
        """
        Encode multiple texts using the SentenceTransformer model.

        Args:
            texts (list): List of texts to encode
            **kwargs: Additional arguments to pass to the model's encode method

        Returns:
            np.ndarray: The embeddings with 1536 dimensions
        """
        return self.encode(texts, **kwargs)

    def encode(self, texts, **kwargs):
        """
        Encode text(s) using the SentenceTransformer model with projection.

        Args:
            texts (str or list): The text(s) to encode
            **kwargs: Additional arguments to pass to the model's encode method

        Returns:
            np.ndarray: The embedding(s) with 1536 dimensions
        """
        if not self.__class__._initialized or self.__class__._model is None:
            logger.error("❌ Cannot encode: SentenceTransformer model not initialized")
            return None

        try:
            # Set default parameters optimized for BGE model
            kwargs.setdefault("batch_size", 8)
            kwargs.setdefault("normalize_embeddings", True)
            kwargs.setdefault("show_progress_bar", False)

            # Generate embeddings with projection to 1536 dimensions
            embeddings = self.__class__._model.encode(texts, **kwargs)

            # Verify dimensions
            if isinstance(texts, list):
                expected_shape = (len(texts), self._output_dim)
            else:
                expected_shape = (self._output_dim,)

            if (
                isinstance(embeddings, np.ndarray)
                and embeddings.shape[-1] != self._output_dim
            ):
                logger.warning(
                    f"⚠️ Unexpected embedding dimensions: {embeddings.shape}, expected: {expected_shape}"
                )
            else:
                logger.debug(
                    f"✅ Generated embeddings with correct dimensions: {embeddings.shape}"
                )

            return embeddings
        except Exception as e:
            logger.error(f"❌ Error encoding text with SentenceTransformer: {str(e)}")
            return None

    def is_initialized(self):
        """
        Check if the model is initialized.

        Returns:
            bool: True if initialized, False otherwise
        """
        return self.__class__._initialized and self.__class__._model is not None

    def get_output_dimension(self):
        """
        Get the output dimension of the model.

        Returns:
            int: The output dimension (1536 for OpenAI compatibility)
        """
        return self._output_dim


# Singleton accessor function
def get_sentence_transformer(model_name=None):
    """
    Get the singleton SentenceTransformer instance with projection layer.

    Args:
        model_name (str, optional): The name of the base SentenceTransformer model to load.
                                   If None, defaults to BGE-large model.

    Returns:
        SentenceTransformerService: The singleton instance with projection layer
    """
    return SentenceTransformerService(model_name)
