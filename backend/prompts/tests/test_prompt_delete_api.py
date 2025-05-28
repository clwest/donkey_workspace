import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from prompts.models import Prompt
from assistants.models import Assistant

class PromptDeleteAPITest(APITestCase):
    def setUp(self):
        self.prompt = Prompt.objects.create(title="Del", content="c", source="t")
        self.url = f"/api/prompts/{self.prompt.slug}/delete/"

    def test_delete_prompt_success(self):
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Prompt.objects.filter(id=self.prompt.id).exists())

    def test_delete_prompt_in_use_blocked(self):
        prompt = Prompt.objects.create(title="used", content="c", source="t")
        Assistant.objects.create(name="A", specialty="x", system_prompt=prompt)
        url = f"/api/prompts/{prompt.slug}/delete/"
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(Prompt.objects.filter(id=prompt.id).exists())

    def test_delete_prompt_force(self):
        prompt = Prompt.objects.create(title="force", content="c", source="t")
        Assistant.objects.create(name="A2", specialty="x", system_prompt=prompt)
        url = f"/api/prompts/{prompt.slug}/delete/?force=true"
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Prompt.objects.filter(id=prompt.id).exists())

