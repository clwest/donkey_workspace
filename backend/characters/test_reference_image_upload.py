import os

# Ensure Django settings are configured for tests
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from characters.models import CharacterProfile, CharacterReferenceImage


class ReferenceImageUploadTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="uploader", password="pw")
        self.client.force_authenticate(user=self.user)
        # Create a character to attach images to
        self.character = CharacterProfile.objects.create(
            name="ImageTest", created_by=self.user
        )

    def test_upload_preview_image_via_url(self):
        """
        Posting a JSON URL should fetch and save the image, associating it with the character.
        """
        image_url = "https://via.placeholder.com/300"
        payload = {
            "character": self.character.id,
            "image": image_url,
        }
        # Use the DRF router list route for reference-images
        url = reverse("characterreferenceimage-list")
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        # Confirm response contains ID and metadata
        self.assertIn("id", data)
        # Confirm DB record exists with correct FK
        ref = CharacterReferenceImage.objects.filter(id=data["id"]).first()
        self.assertIsNotNone(ref)
        self.assertEqual(ref.character_id, self.character.id)
        # Caption and alt_text should be generated based on character info
        expected_caption = f"Preview of {self.character.name}"
        expected_alt_text = f"AI-generated image of {self.character.name}"
        self.assertEqual(ref.caption, expected_caption)
        self.assertEqual(ref.alt_text, expected_alt_text)

    def test_upload_requires_authentication(self):
        """Unauthenticated requests should be rejected."""
        self.client.force_authenticate(user=None)
        url = reverse("characterreferenceimage-list")
        payload = {
            "character": self.character.id,
            "image": "https://via.placeholder.com/300",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
