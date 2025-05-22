
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, CollaborationThread


class CollaborationThreadAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="col2", password="pw")
        self.client.force_authenticate(self.user)
        self.lead = Assistant.objects.create(name="Lead", specialty="x")
        self.other = Assistant.objects.create(name="Other", specialty="y")
        self.url = f"/api/v1/assistants/{self.lead.id}/collaborate/"

    def test_create_thread(self):
        resp = self.client.post(
            self.url,
            {
                "assistant_ids": [str(self.other.id)],
                "messages": [{"role": "user", "content": "hi"}],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        thread_id = resp.json()["thread_id"]
        thread = CollaborationThread.objects.get(id=thread_id)
        self.assertIn(self.other, thread.participants.all())
        self.assertEqual(thread.messages[0]["content"], "hi")
