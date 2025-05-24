from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, AssistantRelayMessage
from unittest.mock import patch


class AssistantRelayAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.a1 = Assistant.objects.create(name="S1", specialty="seer")
        self.a2 = Assistant.objects.create(name="S2", specialty="sage", auto_reflect_on_message=True)

    @patch("assistants.viewsets.assistant_viewset.AssistantReflectionEngine.generate_reflection")
    def test_relay_endpoint(self, mock_reflect):
        mock_reflect.return_value = "reflected"
        url = f"/api/v1/assistants/{self.a1.slug}/relay/"
        resp = self.client.post(
            url,
            {"recipient_slug": self.a2.slug, "message": "ping"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data["sender"], self.a1.slug)
        self.assertEqual(data["recipient"], self.a2.slug)
        msg = AssistantRelayMessage.objects.get(id=data["id"])
        self.assertTrue(msg.delivered)
        self.assertTrue(msg.responded)
        self.assertIsNotNone(msg.thought_log)
