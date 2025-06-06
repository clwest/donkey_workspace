import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, AssistantReflectionLog


class ReflectionPrimerAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(
            name="A", slug="a", created_by=self.user
        )

    def test_reflection_primer(self):
        for i in range(5):
            AssistantReflectionLog.objects.create(
                assistant=self.assistant,
                title=f"r{i}",
                summary="s",
            )
        url = f"/api/assistants/{self.assistant.slug}/reflection_review_primer/"
        resp = self.client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        assert data["assistant"]["name"] == "A"
        assert len(data["reflections"]) == 3
        assert data["full_view"].endswith("/reflections/")
