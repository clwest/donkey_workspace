from unittest.mock import patch
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.models.user_preferences import AssistantUserPreferences
from insights.models import AssistantInsightLog


class SelfNarrationTest(BaseAPITestCase):
    @patch("utils.llm_router.chat")
    def test_self_narration_logged(self, mock_chat):
        mock_chat.return_value = (
            "ok",
            ["m1"],
            {"anchor_hits": ["term"], "reflection_hits": ["r1"]},
            {"used_memories": ["m1"], "anchors": ["term"], "reflections": ["r1"]},
        )
        self.authenticate()
        assistant = Assistant.objects.create(name="A", slug="a")
        AssistantUserPreferences.objects.create(
            user=self.user, assistant=assistant, self_narration_enabled=True
        )
        resp = self.client.post(
            f"/api/assistants/{assistant.slug}/chat/",
            {"message": "hi", "session_id": "s1"},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.data.get("reasoning_trace")
        assert AssistantInsightLog.objects.filter(log_type="self_narration").exists()
