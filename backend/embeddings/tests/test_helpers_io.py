import json
from django.test import SimpleTestCase, override_settings
from unittest.mock import patch, MagicMock

from embeddings.helpers.helpers_io import (
    get_cache,
    set_cache,
    save_embedding,
    retrieve_embeddings,
    queue_for_processing,
)


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "test-cache",
        }
    }
)
class HelpersIOTest(SimpleTestCase):
    def test_cache_set_and_get(self):
        # Setting and getting a key should return the stored value
        set_cache("foo", "bar", timeout=30)
        self.assertEqual(get_cache("foo"), "bar")
        # Missing key returns None
        self.assertIsNone(get_cache("nonexistent"))

    def test_save_embedding_creates_entry(self):
        # Mock Embedding.objects.create to verify save logic
        dummy_emb = MagicMock()
        with patch(
            "embeddings.helpers.helpers_io.Embedding.objects.create",
            return_value=dummy_emb,
        ) as mock_create:
            # Create a dummy object with id and content_type
            class DummyObj:
                pass

            obj = DummyObj()
            obj.id = 42
            obj.content_type = "test_type"
            vec = [0.1, 0.2, 0.3]
            result = save_embedding(obj, vec)
            # Ensure the manager create was called with correct args
            mock_create.assert_called_once_with(
                content_type="test_type", content_id="42", embedding=vec
            )
            # The function should return the created embedding
            self.assertIs(result, dummy_emb)

    def test_retrieve_embeddings_filters_correctly(self):
        # Mock filter to return a list of dummy embeddings
        dummy1 = MagicMock()
        dummy2 = MagicMock()
        with patch(
            "embeddings.helpers.helpers_io.Embedding.objects.filter",
            return_value=[dummy1, dummy2],
        ) as mock_filter:
            results = retrieve_embeddings("doc", ["1", "2", "3"])
            mock_filter.assert_called_once_with(
                content_type="doc", content_id__in=["1", "2", "3"]
            )
            self.assertEqual(results, [dummy1, dummy2])

    def test_queue_for_processing_logs_info(self):
        # Patch the logger to capture info calls
        with patch("embeddings.helpers.helpers_io.logger") as mock_logger:
            queue_for_processing("hello", "doc", "123", model="mymodel")
            # Ensure logger.info was called at least once
            mock_logger.info.assert_called()
            # Verify message content
            msg = mock_logger.info.call_args[0][0]
            self.assertIn("model=mymodel", msg)
            self.assertIn("content_type=doc", msg)
            self.assertIn("content_id=123", msg)
            self.assertIn("text_length=", msg)
