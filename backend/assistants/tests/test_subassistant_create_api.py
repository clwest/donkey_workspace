import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from assistants.models import Assistant
from intel_core.models import Document


class SubAssistantCreateAPITest(APITestCase):
    def setUp(self):
        self.parent = Assistant.objects.create(name="Parent", specialty="p")
        self.doc = Document.objects.create(title="Doc", content="c")
        self.url = f"/api/assistants/{self.parent.id}/sub-assistants/"

    def test_create_subassistant(self):
        resp = self.client.post(
            self.url, {"document_ids": [str(self.doc.id)]}, format="json"
        )
        self.assertEqual(resp.status_code, 200)
        sub_id = resp.json()["sub_assistant_id"]
        self.assertTrue(
            Assistant.objects.filter(id=sub_id, parent_assistant=self.parent).exists()
        )
