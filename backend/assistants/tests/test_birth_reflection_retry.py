from unittest.mock import patch
from requests.exceptions import ConnectionError
from django.core.management import call_command
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.helpers.logging_helper import reflect_on_birth


class BirthReflectionRetryAPITest(BaseAPITestCase):
    @patch("utils.llm_router.call_llm", side_effect=ConnectionError("fail"))
    def test_retry_endpoint_recovers(self, mock_call):
        self.authenticate()
        assistant = Assistant.objects.create(name="R", slug="r")
        reflect_on_birth(assistant)
        assistant.refresh_from_db()
        self.assertFalse(assistant.last_reflection_successful)
        self.assertTrue(assistant.can_retry_birth_reflection)

        mock_call.side_effect = lambda *a, **kw: "ok"
        resp = self.client.post(f"/api/assistants/{assistant.slug}/reflection/retry/")
        self.assertEqual(resp.status_code, 200)
        assistant.refresh_from_db()
        self.assertTrue(assistant.last_reflection_successful)
        self.assertEqual(assistant.birth_reflection_retry_count, 1)
        self.assertFalse(assistant.can_retry_birth_reflection)


class BirthReflectionRetryCommandTest(BaseAPITestCase):
    @patch("utils.llm_router.call_llm", side_effect=ConnectionError("fail"))
    def test_command_retries(self, mock_call):
        assistant = Assistant.objects.create(name="C", slug="c")
        reflect_on_birth(assistant)
        assistant.refresh_from_db()
        self.assertFalse(assistant.last_reflection_successful)

        mock_call.side_effect = lambda *a, **kw: "ok"
        call_command("retry_birth_reflection", assistant.slug)
        assistant.refresh_from_db()
        self.assertTrue(assistant.last_reflection_successful)
        self.assertEqual(assistant.birth_reflection_retry_count, 1)
