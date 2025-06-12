import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from memory.models import MemoryEntry


class OnboardingDebugTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="debug", password="pw")
        self.client.force_authenticate(user=self.user)

    def test_intro_memory_and_debug_endpoint(self):
        # Complete all steps
        for step in [
            "mythpath",
            "world",
            "glossary",
            "archetype",
            "summon",
            "personality",
            "wizard",
            "ritual",
        ]:
            self.client.post("/api/onboarding/complete/", {"step": step}, format="json")

        debug_data = self.client.get("/api/onboarding/debug/").json()
        self.assertTrue(debug_data["onboarding_complete"])
        slug = debug_data["primary_assistant_slug"]
        self.assertIsNotNone(slug)

        intro_exists = MemoryEntry.objects.filter(
            assistant__slug=slug, type="assistant_intro"
        ).exists()
        self.assertTrue(intro_exists)
        self.assertTrue(debug_data["intro_memory_created"])
