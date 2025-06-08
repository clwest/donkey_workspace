
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
        resp = self.client.get("/api/v1/assistants/primary/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["id"], str(a.id))
        self.assertIn("recent_thoughts", data)

    def test_no_primary_returns_404(self):
        Assistant.objects.create(name="A1", specialty="s")
        resp = self.client.get("/api/v1/assistants/primary/")
        self.assertEqual(resp.status_code, 404)

    def test_no_assistants_returns_204(self):
        resp = self.client.get("/api/v1/assistants/primary/")
        self.assertEqual(resp.status_code, 204)

    def test_auto_unset_existing_primary_on_create(self):
        first = Assistant.objects.create(name="A1", specialty="x", is_primary=True)
        second = Assistant.objects.create(name="A2", specialty="y", is_primary=True)
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertFalse(first.is_primary)
        self.assertTrue(second.is_primary)

    def test_assign_primary_endpoint(self):
        a1 = Assistant.objects.create(name="A1", specialty="x", is_primary=True)
        a2 = Assistant.objects.create(name="A2", specialty="y")
        url = f"/api/v1/assistants/{a2.slug}/assign-primary/"
        resp = self.client.patch(url)
        self.assertEqual(resp.status_code, 200)
        a1.refresh_from_db()
        a2.refresh_from_db()
        self.assertFalse(a1.is_primary)
        self.assertTrue(a2.is_primary)

    def test_create_primary_assistant(self):
        resp = self.client.post("/api/assistants/primary/create/")
        self.assertIn(resp.status_code, [200, 201])
        data = resp.json()
        self.assertTrue(data["is_primary"])
        self.assertEqual(Assistant.objects.filter(is_primary=True).count(), 1)
