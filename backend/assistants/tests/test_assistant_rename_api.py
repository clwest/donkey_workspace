from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, AssistantThoughtLog

class AssistantRenameAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="Old Name", specialty="x")
        self.url = f"/api/v1/assistants/{self.assistant.slug}/"

    def test_rename_generates_slug(self):
        resp = self.client.patch(self.url, {"name": "New Name"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assistant.refresh_from_db()
        self.assertEqual(self.assistant.name, "New Name")
        self.assertEqual(self.assistant.slug, "new-name")
        self.assertTrue(
            AssistantThoughtLog.objects.filter(
                assistant=self.assistant,
                thought_type="meta",
                thought__icontains="renamed",
            ).exists()
        )

    def test_slug_collision_rejected(self):
        other = Assistant.objects.create(name="Existing", specialty="x")
        resp = self.client.patch(self.url, {"slug": other.slug}, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assistant.refresh_from_db()
        self.assertNotEqual(self.assistant.slug, other.slug)
