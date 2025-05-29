from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from agents.models.lore import SwarmMemoryEntry
from agents.models.coordination import DirectiveMemoryNode


class DreamInitiateAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(
            name="Dreamer", specialty="dream", dream_symbol="mirror"
        )
        self.url = f"/api/v1/assistants/{self.assistant.id}/dream/initiate/"

    def test_dream_initiates_memory(self):
        resp = self.client.post(self.url, {"dream": "origin"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(SwarmMemoryEntry.objects.filter(origin="dream").exists())
        self.assertTrue(
            DirectiveMemoryNode.objects.filter(assistant=self.assistant).exists()
        )
