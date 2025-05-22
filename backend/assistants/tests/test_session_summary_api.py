
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import (
    Assistant,
    ChatSession,
    AssistantThoughtLog,
    DelegationEvent,
)


class SessionSummaryAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="sum", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A", specialty="root")
        self.session = ChatSession.objects.create(assistant=self.assistant)
        AssistantThoughtLog.objects.create(
            assistant=self.assistant,
            thought="hello",
            narrative_thread=self.session.narrative_thread,
        )
        self.child = Assistant.objects.create(name="B", specialty="child")
        DelegationEvent.objects.create(
            parent_assistant=self.assistant,
            child_assistant=self.child,
            triggering_session=self.session,
            reason="r",
        )

    def test_session_summary_endpoint(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/session-summary/{self.session.session_id}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("entries", data)
        types = {e["type"] for e in data["entries"]}
        self.assertIn("thought", types)
        self.assertIn("delegation", types)
