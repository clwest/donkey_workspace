"""
Tests for the SentenceTransformer service with projection layer.

This module tests that the SentenceTransformer service correctly:
1. Initializes the BGE-Large model with projection layer
2. Produces embeddings with the expected 1536 dimensions
3. Maintains the singleton pattern
4. Handles various input types correctly
"""

import unittest
import numpy as np
from unittest.mock import patch, MagicMock
import torch
import os

from embeddings.sentence_transformer_service import (
    SentenceTransformerService,
    get_sentence_transformer,
)
from embeddings.models import EMBEDDING_LENGTH


class TestSentenceTransformerService(unittest.TestCase):
    """Test cases for SentenceTransformer service with projection layer."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for all test cases."""
        # This can be slow, so we'll test with a smaller model in unit tests
        cls.test_model_name = "all-MiniLM-L6-v2"  # Smaller model for faster testing

    def test_singleton_pattern(self):
        """Test that the service follows the singleton pattern."""
        service1 = get_sentence_transformer(self.test_model_name)
        service2 = get_sentence_transformer(self.test_model_name)
        self.assertIs(
            service1, service2, "Service instances should be identical (singleton)"
        )

    @patch("sentence_transformers.SentenceTransformer")
    def test_initialization_with_projection(self, mock_transformer):
        """Test that initialization includes creation of the projection layer."""
        # Mock the SentenceTransformer class
        mock_model = MagicMock()
        mock_transformer.return_value = mock_model

        # Create a new service instance
        with patch.object(SentenceTransformerService, "_instance", None):
            service = SentenceTransformerService(self.test_model_name)
            self.assertEqual(
                service.get_output_dimension(),
                EMBEDDING_LENGTH,
                f"Output dimension should be {EMBEDDING_LENGTH}",
            )

    @patch.object(SentenceTransformerService, "_init_model_with_projection")
    def test_output_dimension(self, mock_init):
        """Test that the output dimension is set correctly."""
        # Force recreation of singleton
        with patch.object(SentenceTransformerService, "_instance", None):
            service = SentenceTransformerService(self.test_model_name)
            self.assertEqual(
                service.get_output_dimension(),
                EMBEDDING_LENGTH,
                f"Output dimension should be {EMBEDDING_LENGTH}",
            )

    @unittest.skip("Slow test that requires downloading models - run manually")
    def test_embedding_dimensions_real(self):
        """Test that the embeddings have the correct dimensions (requires model download)."""
        service = get_sentence_transformer(self.test_model_name)
        test_text = "This is a test sentence for embedding generation."

        # Single text embedding
        embedding = service.encode(test_text)
        self.assertIsInstance(
            embedding, np.ndarray, "Embedding should be a numpy array"
        )
        self.assertEqual(
            embedding.shape,
            (EMBEDDING_LENGTH,),
            f"Embedding should have {EMBEDDING_LENGTH} dimensions",
        )

        # Multiple texts embeddings
        texts = ["First test sentence.", "Second test sentence."]
        embeddings = service.encode(texts)
        self.assertIsInstance(
            embeddings, np.ndarray, "Embeddings should be a numpy array"
        )
        self.assertEqual(
            embeddings.shape,
            (2, EMBEDDING_LENGTH),
            f"Embeddings should have shape (2, {EMBEDDING_LENGTH})",
        )

    def test_mock_encoding(self):
        """Test encoding with mocked model."""
        # Create a mock model
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([0.1, 0.2, 0.3, 0.4])

        # Patch the _model class variable
        with patch.object(SentenceTransformerService, "_model", mock_model):
            with patch.object(SentenceTransformerService, "_initialized", True):
                # Get the service instance
                service = SentenceTransformerService()

                # Test encoding
                result = service.encode("Test")

                # Verify the mock was called
                mock_model.encode.assert_called_once()

                # Check the result
                self.assertIsInstance(result, np.ndarray)
                self.assertEqual(result.shape, (4,))
                np.testing.assert_array_almost_equal(
                    result, np.array([0.1, 0.2, 0.3, 0.4])
                )

    def test_error_handling(self):
        """Test handling of errors during encoding."""
        # Create a mock model that raises an exception
        mock_model = MagicMock()
        mock_model.encode.side_effect = RuntimeError("Test error")

        # Patch the _model class variable
        with patch.object(SentenceTransformerService, "_model", mock_model):
            with patch.object(SentenceTransformerService, "_initialized", True):
                # Get the service instance
                service = SentenceTransformerService()

                # Test encoding with error
                with self.assertLogs(level="ERROR") as log:
                    result = service.encode("Test")

                # Verify the mock was called
                mock_model.encode.assert_called_once()

                # Check the result is None due to the error
                self.assertIsNone(result)

                # Check that the error was logged
                self.assertTrue(any("Error encoding text" in msg for msg in log.output))


if __name__ == "__main__":
    unittest.main()
