
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.models import AssistantThoughtLog

class PrimaryAssistantAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="viewer", password="pw")
        self.client.force_authenticate(user=self.user)

    def test_primary_endpoint_returns_assistant(self):
        a = Assistant.objects.create(name="Boss", specialty="manage", is_primary=True)
        AssistantThoughtLog.objects.create(assistant=a, thought="hi")
        resp = self.client.get("/api/assistants/primary/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["id"], str(a.id))
        self.assertIn("recent_thoughts", data)

    def test_no_primary_returns_404(self):
        Assistant.objects.create(name="A1", specialty="s")
        resp = self.client.get("/api/assistants/primary/")
        self.assertEqual(resp.status_code, 404)

    def test_unique_primary_validation(self):
        Assistant.objects.create(name="A1", specialty="x", is_primary=True)
        with self.assertRaises(ValidationError):
            Assistant(name="A2", specialty="y", is_primary=True).save()
