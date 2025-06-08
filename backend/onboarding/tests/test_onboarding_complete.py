import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from onboarding.config import STEPS
from accounts.models import UserOnboardingProgress

class OnboardingCompleteTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="complete", password="pw")
        self.client.force_authenticate(user=self.user)

    def test_complete_only_once(self):
        resp = self.client.post("/api/onboarding/complete/", {}, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["onboarding_complete"])
        progress_count = UserOnboardingProgress.objects.filter(
            user=self.user, status="completed"
        ).count()
        self.assertEqual(progress_count, len(STEPS))

        resp2 = self.client.post("/api/onboarding/complete/", {}, format="json")
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()
        self.assertTrue(data2["onboarding_complete"])
        progress_count2 = UserOnboardingProgress.objects.filter(
            user=self.user, status="completed"
        ).count()
        self.assertEqual(progress_count2, len(STEPS))

        info = self.client.get("/api/user/").json()
        self.assertTrue(info["onboarding_complete"])
