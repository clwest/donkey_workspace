import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from memory.models import MemoryEntry


class LinkDiagnosticsAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="Diag", specialty="g")
        MemoryEntry.objects.create(event="a", assistant=self.assistant)
        other = Assistant.objects.create(name="Other", specialty="g")
        MemoryEntry.objects.create(event="b", assistant=other, context=self.assistant.memory_context)

    def test_diagnostics_endpoint(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/link_diagnostics/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("orphaned", data)
        self.assertIn("conflicting", data)
