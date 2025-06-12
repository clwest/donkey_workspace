import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from assistants.models import Assistant


class AssistantRoutingDebugAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="debug", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(
            name="DebugA",
            specialty="general",
            created_by=self.user,
            is_primary=True,
        )
        self.user.primary_assistant_slug = self.assistant.slug
        self.user.onboarding_complete = True
        self.user.save(update_fields=["primary_assistant_slug", "onboarding_complete"])

    def test_debug_endpoint(self):
        resp = self.client.get("/api/debug/assistant_routing/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["onboarding_complete"], True)
        self.assertEqual(data["primary_slug"], self.assistant.slug)

    def test_unauthenticated(self):
        self.client.logout()
        resp = self.client.get("/api/debug/assistant_routing/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertFalse(data["onboarding_complete"])
        self.assertIsNone(data["primary_slug"])
