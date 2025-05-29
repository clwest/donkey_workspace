from assistants.tests import BaseAPITestCase
from assistants.models import Assistant


class AssistantOnboardAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="New", specialty="dream")
        self.url = f"/api/v1/assistants/{self.assistant.id}/onboard/"

    def test_onboard_updates_fields(self):
        payload = {
            "archetype": "sage",
            "dream_symbol": "flame",
            "init_reflection": "awakening",
        }
        resp = self.client.post(self.url, payload, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assistant.refresh_from_db()
        self.assertEqual(self.assistant.archetype, "sage")
        self.assertEqual(self.assistant.dream_symbol, "flame")
        self.assertEqual(self.assistant.init_reflection, "awakening")
