from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from memory.models import RAGGroundingLog
from unittest.mock import patch


class RagLogCreationTest(BaseAPITestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Chat", specialty="s")
        self.url = f"/api/v1/assistants/{self.assistant.slug}/chat/"
        self.client.force_authenticate(user=self.authenticate())

    @patch("utils.llm_router.chat")
    def test_log_created_with_debug(self, mock_chat):
        mock_chat.return_value = (
            "ok",
            [],
            {
                "used_chunks": [{"chunk_id": "c1", "score": 0.9}],
                "rag_fallback": False,
                "retrieval_score": 0.9,
                "anchor_hits": ["a1"],
                "anchor_misses": [],
                "fallback_reason": None,
            },
        )
        resp = self.client.post(
            self.url + "?debug=true",
            {"message": "hi", "session_id": "s1"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        log = RAGGroundingLog.objects.filter(assistant=self.assistant).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.used_chunk_ids, ["c1"])

