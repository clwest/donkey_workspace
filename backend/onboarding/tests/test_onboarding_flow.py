import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from onboarding.config import STEPS


class OnboardingFlowTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="flow", password="pw")
        self.client.force_authenticate(user=self.user)

    def test_onboarding_completion_updates_user(self):
        for step in STEPS:
            resp = self.client.post("/api/onboarding/complete/", {"step": step}, format="json")
            self.assertEqual(resp.status_code, 200)
            info = self.client.get("/api/user/").json()
            if step == STEPS[-1]:
                self.assertTrue(info["onboarding_complete"])
                self.user.refresh_from_db()
                self.assertTrue(self.user.onboarding_complete)
            else:
                self.assertFalse(info["onboarding_complete"])
