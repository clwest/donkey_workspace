import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from prompts.models import Prompt


class PromptUpdateAPITest(APITestCase):
    def setUp(self):
        self.prompt = Prompt.objects.create(title="Base", content="Hello", source="test")

    def test_update_prompt_success(self):
        url = f"/api/prompts/{self.prompt.slug}/update/"
        resp = self.client.patch(url, {"title": "New"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.prompt.refresh_from_db()
        self.assertEqual(self.prompt.title, "New")

    def test_update_prompt_not_found(self):
        url = "/api/prompts/does-not-exist/update/"
        resp = self.client.patch(url, {"title": "X"}, format="json")
        self.assertEqual(resp.status_code, 404)
