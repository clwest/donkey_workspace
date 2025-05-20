import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from assistants.models import Assistant, ChatSession, AssistantChatMessage, SessionHandoff


class SessionHandoffAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="handoff", password="pw")
        self.client.force_authenticate(user=self.user)
        self.a1 = Assistant.objects.create(name="A1", specialty="s1")
        self.a2 = Assistant.objects.create(name="A2", specialty="s2")
        self.session = ChatSession.objects.create(assistant=self.a1)
        for i in range(4):
            AssistantChatMessage.objects.create(
                session=self.session,
                role="user" if i % 2 == 0 else "assistant",
                content=f"m{i}"
            )

    def test_create_and_list_handoff(self):
        url = "/api/assistants/handoff/"
        resp = self.client.post(
            url,
            {
                "from": self.a1.slug,
                "to": self.a2.slug,
                "session_id": str(self.session.session_id),
                "reason": "escalation",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertIn("handoff_summary", data)
        self.assertEqual(SessionHandoff.objects.count(), 1)

        list_url = f"/api/assistants/handoff/{self.session.session_id}/"
        resp2 = self.client.get(list_url)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(resp2.json()), 1)
        self.assertEqual(resp2.json()[0]["reason"], "escalation")
