from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, ChatSession
from prompts.models import Prompt
from project.models import Project

class AssistantDeleteAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="DelA", specialty="x")
        self.url = f"/api/v1/assistants/{self.assistant.slug}/"

    def test_delete_blocked_with_project(self):
        Project.objects.create(user=self.user, title="P", assistant=self.assistant)
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(Assistant.objects.filter(id=self.assistant.id).exists())

    def test_delete_force_cascades(self):
        ChatSession.objects.create(assistant=self.assistant)
        Project.objects.create(user=self.user, title="P2", assistant=self.assistant)
        resp = self.client.delete(self.url + "?force=true")
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Assistant.objects.filter(id=self.assistant.id).exists())
        self.assertEqual(ChatSession.objects.filter(assistant=self.assistant).count(), 0)
        self.assertEqual(Project.objects.filter(assistant=self.assistant).count(), 0)

    def test_delete_cascade_children(self):
        child = Assistant.objects.create(name="Child", specialty="c", parent_assistant=self.assistant)
        resp = self.client.delete(self.url + "?cascade=true")
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Assistant.objects.filter(id=self.assistant.id).exists())
        self.assertFalse(Assistant.objects.filter(id=child.id).exists())

