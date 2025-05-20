import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from assistants.models import Assistant, AssistantThoughtLog, AssistantReflectionInsight
from intel_core.models import Document


class AssistantAddDocumentAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="doc", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="DocA", specialty="s")
        self.document = Document.objects.create(
            title="Doc1", content="text", source_type="url"
        )

    def test_add_document_and_reflect(self):
        url = f"/api/assistants/{self.assistant.slug}/add_document/"
        resp = self.client.post(
            url,
            {"document_id": str(self.document.id), "reflect": True},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assistant.refresh_from_db()
        self.assertIn(self.document, self.assistant.documents.all())
        self.assertEqual(
            AssistantThoughtLog.objects.filter(assistant=self.assistant).count(), 1
        )
        self.assertGreater(
            AssistantReflectionInsight.objects.filter(assistant=self.assistant).count(),
            0,
        )

    def test_duplicate_link(self):
        self.assistant.documents.add(self.document)
        url = f"/api/assistants/{self.assistant.slug}/add_document/"
        resp = self.client.post(
            url, {"document_id": str(self.document.id)}, format="json"
        )
        self.assertEqual(resp.status_code, 400)
