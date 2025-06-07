import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, AssistantReflectionLog
from memory.models import MemoryEntry


class FirstReflectionAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(
            name="A", slug="a", created_by=self.user
        )

    def test_first_reflection_endpoint(self):
        for i in range(6):
            MemoryEntry.objects.create(
                event=f"m{i}", assistant=self.assistant, source_role="user"
            )
        url = f"/api/assistants/{self.assistant.slug}/reflect_first_use/"
        resp = self.client.post(url, format="json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary"]
        log = AssistantReflectionLog.objects.get(id=data["id"])
        assert log.is_primer
        assert len(log.generated_from_memory_ids) == 6
