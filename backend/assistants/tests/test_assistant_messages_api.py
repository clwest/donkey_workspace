import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from assistants.models import Assistant, AssistantMessage


class AssistantMessagesAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="sender", password="pw")
        self.client.force_authenticate(user=self.user)
        self.a1 = Assistant.objects.create(name="A1", specialty="s1")
        self.a2 = Assistant.objects.create(name="A2", specialty="s2")

    def test_send_and_list_messages(self):
        url = "/api/assistants/messages/send/"
        resp = self.client.post(url, {
            "sender": self.a1.slug,
            "recipient": self.a2.slug,
            "content": "hello",
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        msg_id = resp.json()["id"]
        inbox = self.client.get(f"/api/assistants/messages/inbox/{self.a2.slug}")
        outbox = self.client.get(f"/api/assistants/messages/outbox/{self.a1.slug}")
        self.assertEqual(inbox.status_code, 200)
        self.assertEqual(outbox.status_code, 200)
        self.assertEqual(len(inbox.json()), 1)
        self.assertEqual(len(outbox.json()), 1)
        self.assertEqual(inbox.json()[0]["id"], msg_id)
        self.assertEqual(outbox.json()[0]["id"], msg_id)

