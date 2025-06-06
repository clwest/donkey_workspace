import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from assistants.tests import BaseAPITestCase


class OnboardingProgressAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()

    def test_progress_endpoints(self):
        resp = self.client.get("/api/onboarding/status/")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        data = body["progress"]
        self.assertEqual(body["percent"], 0)
        self.assertEqual(body["next_step"], "mythpath")
        self.assertEqual(data[0]["step"], "mythpath")
        self.assertEqual(data[0]["status"], "pending")

        resp = self.client.post(
            "/api/onboarding/complete/",
            {"step": "mythpath"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        data = body["progress"]
        self.assertEqual(body["percent"], 16)
        self.assertEqual(body["next_step"], "world")
        self.assertEqual(data[0]["status"], "completed")

        resp = self.client.get("/api/onboarding/status/")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        data = body["progress"]
        self.assertEqual(body["next_step"], "world")
        self.assertEqual(data[0]["status"], "completed")
