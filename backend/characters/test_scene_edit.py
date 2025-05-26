import os

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from characters.models import CharacterProfile, CharacterReferenceImage
from images.models import Image as SceneImage


class SceneEditBaseImageTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pw")
        self.client.force_authenticate(user=self.user)
        self.character = CharacterProfile.objects.create(
            name="Tester", created_by=self.user
        )
        self.ref_image = CharacterReferenceImage.objects.create(
            character=self.character,
            image=SimpleUploadedFile("img.jpg", b"data", content_type="image/jpeg"),
        )

    @patch("characters.views.save_edited_image", return_value="edited_images/out.webp")
    @patch("characters.views.requests.post")
    def test_scene_edit_with_base_image(self, mock_post, mock_save):
        mock_post.return_value.status_code = 200
        mock_post.return_value.content = b"image"
        url = reverse(
            "characterprofile-scene-edit", kwargs={"slug": self.character.slug}
        )
        resp = self.client.post(
            url,
            {"prompt": "hello", "base_image_id": self.ref_image.id},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        img = SceneImage.objects.filter(character=self.character).first()
        self.assertIsNotNone(img)
        self.assertEqual(img.status, "completed")
        self.assertEqual(img.file_path, "edited_images/out.webp")

    def test_scene_edit_invalid_base_image(self):
        url = reverse(
            "characterprofile-scene-edit", kwargs={"slug": self.character.slug}
        )
        resp = self.client.post(
            url,
            {"prompt": "oops", "base_image_id": 9999},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
