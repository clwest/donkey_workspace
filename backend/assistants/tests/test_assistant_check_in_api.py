
from assistants.tests import BaseAPITestCase
from unittest.mock import patch, MagicMock
from assistants.models import Assistant


class AssistantCheckInAPITest(BaseAPITestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Helper", specialty="h")
        self.url = f"/api/v1/assistants/{self.assistant.id}/check-in/"

    @patch("assistants.views.check_in.client")
    def test_check_in_returns_suggestions(self, mock_client):
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock(message=MagicMock(content="Do tasks"))]
        mock_client.chat.completions.create.return_value = mock_resp
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["suggestions"], "Do tasks")
