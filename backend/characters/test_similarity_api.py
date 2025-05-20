import hashlib
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch

from characters.models import CharacterProfile
from embeddings.models import Embedding


class CharacterSimilarityAPITest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="user1", password="pw")
        self.other = User.objects.create_user(username="user2", password="pw")

        # Create characters
        self.char_public = CharacterProfile.objects.create(
            name="Public", created_by=self.user, is_public=True
        )
        self.char_private_self = CharacterProfile.objects.create(
            name="Self", created_by=self.user, is_public=False
        )
        self.char_private_other = CharacterProfile.objects.create(
            name="Other", created_by=self.other, is_public=False
        )

        # Create embeddings for characters
        dim = Embedding._meta.get_field("embedding").dimensions
        v_public = [1.0] + [0.0] * (dim - 1)
        Embedding.objects.create(
            content_type="characterprofile",
            content_id=str(self.char_public.id),
            embedding=v_public,
        )
        Embedding.objects.create(
            content_type="characterprofile",
            content_id=str(self.char_private_self.id),
            embedding=v_public,
        )
        Embedding.objects.create(
            content_type="characterprofile",
            content_id=str(self.char_private_other.id),
            embedding=v_public,
        )

        # Authenticated client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_similarity_includes_only_allowed_characters(self):
        # Mock generate_embedding to return v_public
        dim = Embedding._meta.get_field("embedding").dimensions
        v_public = [1.0] + [0.0] * (dim - 1)
        with patch(
            "embeddings.helpers.helpers_processing.generate_embedding",
            return_value=v_public,
        ):
            resp = self.client.post(
                "/api/v1/characters/similarity/", {"text": "test"}, format="json"
            )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in resp.json()]
        self.assertIn(self.char_public.id, ids)
        self.assertIn(self.char_private_self.id, ids)
        self.assertNotIn(self.char_private_other.id, ids)

    def test_caching_behavior(self):
        text = "cache test"
        fingerprint = hashlib.sha256(text.encode()).hexdigest()
        cache_key = f"char-sim:{fingerprint}"
        cache.delete(cache_key)

        resp1 = self.client.post(
            "/api/v1/characters/similarity/", {"text": text}, format="json"
        )
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(cache.get(cache_key))

        # Bypass cache
        cache.delete(cache_key)
        resp2 = self.client.post(
            f"/api/v1/characters/similarity/?nocache=true",
            {"text": text},
            format="json",
        )
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertIsNone(cache.get(cache_key))

    def test_unauthenticated_denied(self):
        unauth = APIClient()
        resp = unauth.post(
            "/api/v1/characters/similarity/", {"text": "test"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
