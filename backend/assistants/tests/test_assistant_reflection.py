from unittest.mock import patch
from requests.exceptions import ConnectionError
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.helpers.logging_helper import reflect_on_birth


class BirthReflectionFallbackTest(BaseAPITestCase):
    @patch("utils.llm_router.call_llm", side_effect=ConnectionError("fail"))
    def test_connection_error_sets_metadata(self, mock_call):
        assistant = Assistant.objects.create(name="A", slug="a")
        reflect_on_birth(assistant)
        assistant.refresh_from_db()
        assert assistant.last_reflection_attempted_at is not None
        assert assistant.last_reflection_successful is False
        assert assistant.reflection_error

    @patch("utils.llm_router.call_llm", side_effect=ConnectionError("fail"))
    def test_metadata_exposed_in_api(self, mock_call):
        self.authenticate()
        assistant = Assistant.objects.create(name="B", slug="b")
        reflect_on_birth(assistant)
        resp = self.client.get(f"/api/assistants/{assistant.slug}/")
        data = resp.json()
        assert data["last_reflection_successful"] is False
        assert data["reflection_error"]
