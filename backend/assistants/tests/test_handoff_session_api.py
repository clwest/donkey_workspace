
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, ChatSession, DelegationEvent, AssistantChatMessage, AssistantThoughtLog

class HandoffSessionAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="handoff", password="pw")
        self.client.force_authenticate(user=self.user)
        self.parent = Assistant.objects.create(name="Parent", specialty="root")
        self.child = Assistant.objects.create(name="Logic Llama", specialty="logic")
        self.session = ChatSession.objects.create(assistant=self.parent)

    def test_handoff_endpoint(self):
        url = f"/api/assistants/{self.parent.slug}/handoff/"
        resp = self.client.post(
            url,
            {
                "target_slug": self.child.slug,
                "reason": "deep reasoning required",
                "session_id": self.session.session_id,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.session.refresh_from_db()
        self.assertEqual(self.session.assistant, self.child)
        event = DelegationEvent.objects.get()
        self.assertTrue(event.handoff)
        self.assertEqual(event.parent_assistant, self.parent)
        self.assertEqual(event.child_assistant, self.child)
        self.assertTrue(
            AssistantThoughtLog.objects.filter(
                assistant=self.parent, thought_type="handoff"
            ).exists()
        )
        self.assertTrue(
            AssistantThoughtLog.objects.filter(
                assistant=self.child, thought_type="resumed_session"
            ).exists()
        )
        self.assertTrue(
            AssistantChatMessage.objects.filter(session=self.session, message_type="system").exists()
        )

