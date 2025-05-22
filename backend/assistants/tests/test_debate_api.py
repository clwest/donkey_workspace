
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant


class DebateAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="debater", password="pw")
        self.client.force_authenticate(user=self.user)
        self.a1 = Assistant.objects.create(name="A1", specialty="s1")
        self.a2 = Assistant.objects.create(name="A2", specialty="s2")

    def test_start_debate_flow(self):
        url = "/api/assistants/debate/start/"
        data = {
            "topic": "Test Topic",
            "arguments": [
                {"assistant": self.a1.slug, "position": "agree", "content": "ok"},
                {"assistant": self.a2.slug, "position": "disagree", "content": "no"},
            ],
        }
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, 201)
        debate_id = resp.json()["id"]

        resp2 = self.client.post(
            f"/api/assistants/debate/{debate_id}/respond/",
            {
                "assistant": self.a1.slug,
                "position": "expand",
                "content": "more",
            },
            format="json",
        )
        self.assertEqual(resp2.status_code, 201)
        self.assertEqual(resp2.json()["round"], 2)

        resp3 = self.client.post(
            f"/api/assistants/debate/{debate_id}/consensus/",
            {"assistant": self.a1.slug},
            format="json",
        )
        self.assertEqual(resp3.status_code, 201)
        self.assertIn("summary", resp3.json())
