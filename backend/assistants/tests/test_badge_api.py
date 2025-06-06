from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, Badge


class BadgeAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="badge", password="pw")
        self.client.force_authenticate(self.user)
        self.assistant = Assistant.objects.create(name="Skill", specialty="t")
        Badge.objects.create(slug="reflection_ready", label="Ready", criteria="5 reflections")

    def test_list_badges(self):
        resp = self.client.get("/api/v1/assistants/badges/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

    def test_update_badges(self):
        resp = self.client.post(f"/api/v1/assistants/{self.assistant.slug}/update_badges/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("updated", resp.json())
