from unittest.mock import patch
from requests.exceptions import ConnectionError
from django.core.management import call_command
import io
import json
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

    @patch("utils.llm_router.call_llm", side_effect=ConnectionError("fail"))
    def test_retry_endpoint_uuid(self, mock_call):
        self.authenticate()
        assistant = Assistant.objects.create(name="U", slug="u")
        reflect_on_birth(assistant)
        assistant.refresh_from_db()
        mock_call.side_effect = lambda *a, **kw: "ok"
        resp = self.client.post(
            f"/api/assistants/{assistant.id}/reflection/retry/"
        )
        self.assertEqual(resp.status_code, 200)
        assistant.refresh_from_db()
        self.assertTrue(assistant.last_reflection_successful)


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

    @patch("utils.llm_router.call_llm", side_effect=ConnectionError("fail"))
    def test_command_all_flag(self, mock_call):
        a = Assistant.objects.create(name="A", slug="a")
        reflect_on_birth(a)
        a.refresh_from_db()
        mock_call.side_effect = lambda *a, **kw: "ok"
        call_command("retry_birth_reflection", "--all")
        a.refresh_from_db()
        self.assertTrue(a.last_reflection_successful)


class AuditBirthReflectionCommandTest(BaseAPITestCase):
    def test_audit_json(self):
        assistant = Assistant.objects.create(
            name="D", slug="d", birth_reflection_retry_count=2
        )
        out = io.StringIO()
        call_command("audit_birth_reflections", "--json", stdout=out)
        data = json.loads(out.getvalue())
        self.assertEqual(data[0]["slug"], assistant.slug)
