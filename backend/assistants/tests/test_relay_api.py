from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, AssistantRelayMessage


class AssistantRelayAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.a1 = Assistant.objects.create(name="S1", specialty="seer")
        self.a2 = Assistant.objects.create(name="S2", specialty="sage", auto_reflect_on_message=True)

    def test_relay_endpoint(self):
        url = f"/api/v1/assistants/{self.a1.slug}/relay/"
        resp = self.client.post(url, {"recipient_slug": self.a2.slug, "message": "ping"}, format="json")
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data["sender"], self.a1.slug)
        self.assertEqual(data["recipient"], self.a2.slug)
        msg = AssistantRelayMessage.objects.get(id=data["id"])
        self.assertEqual(msg.status, "delivered")
        self.assertEqual(self.a2.thoughts.filter(role="relay").count(), 1)
