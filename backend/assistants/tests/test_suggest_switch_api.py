from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, ChatSession


class SuggestSwitchAPITest(BaseAPITestCase):
    def setUp(self):
        self.user = self.authenticate()
        self.a1 = Assistant.objects.create(name="A1")
        self.a2 = Assistant.objects.create(name="A2")
        self.session = ChatSession.objects.create(assistant=self.a1, session_id="s1")

    def test_suggest_switch_endpoint(self):
        url = "/api/assistants/suggest_switch/"
        resp = self.client.post(url, {"session_id": "s1"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("suggested_assistant", resp.json())
