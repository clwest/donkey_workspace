from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from unittest.mock import patch

from characters.models import CharacterProfile
from images.models import Image

class SceneEditViewTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="char", password="pw")
        self.client.force_authenticate(user=self.user)
        self.char = CharacterProfile.objects.create(name="Hero", slug="hero", created_by=self.user)

    @patch("characters.views.process_sd_image_request.delay")
    def test_scene_edit_basic(self, mock_delay):
        url = f"/api/v1/characters/profiles/{self.char.slug}/scene-edit/"
        resp = self.client.post(url, {"prompt": "a sunny day"}, format="json")
        self.assertEqual(resp.status_code, 201)
        img = Image.objects.filter(character=self.char).first()
        self.assertIsNotNone(img)
        self.assertEqual(img.generation_type, "scene")
        mock_delay.assert_called_once_with(img.id)

    @patch("characters.views.process_sd_image_request.delay")
    def test_scene_edit_with_base_image(self, mock_delay):
        base = Image.objects.create(user=self.user, prompt="base", order=0)
        url = f"/api/v1/characters/profiles/{self.char.slug}/scene-edit/"
        resp = self.client.post(url, {"prompt": "a forest", "base_image_id": base.id}, format="json")
        self.assertEqual(resp.status_code, 201)
        img = Image.objects.filter(character=self.char).order_by("-created_at").first()
        self.assertIsNotNone(img)
        mock_delay.assert_called_once_with(img.id)

