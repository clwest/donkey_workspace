import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from assistants.tests import BaseAPITestCase
from django.contrib.auth import get_user_model


class FeedbackAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()

    def test_post_feedback(self):
        resp = self.client.post(
            "/api/feedback/",
            {"assistant_slug": "demo", "category": "bug", "description": "oops"},
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data["assistant_slug"], "demo")
        self.assertEqual(data["category"], "bug")
        self.assertEqual(data["description"], "oops")

    def test_list_feedback(self):
        self.client.post(
            "/api/feedback/",
            {"assistant_slug": "demo", "category": "idea", "description": "add"},
        )
        resp = self.client.get("/api/feedback/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
