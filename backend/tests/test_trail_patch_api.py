import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.models.trail import TrailMarkerLog


class TrailPatchAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()

    def test_patch_trail_marker(self):
        asst = Assistant.objects.create(name="T", slug="t", created_by=self.user)
        marker = TrailMarkerLog.objects.create(assistant=asst, marker_type="birth")
        url = f"/api/trail/{marker.id}/"
        resp = self.client.patch(
            url,
            {
                "user_note": "hello",
                "user_emotion": "💡",
                "is_starred": True,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        marker.refresh_from_db()
        self.assertEqual(marker.user_note, "hello")
        self.assertEqual(marker.user_emotion, "💡")
        self.assertTrue(marker.is_starred)

    def test_patch_forbidden(self):
        asst = Assistant.objects.create(name="A", slug="a", created_by=self.user)
        marker = TrailMarkerLog.objects.create(assistant=asst, marker_type="birth")
        from django.contrib.auth import get_user_model
        other = get_user_model().objects.create_user(username="o", password="pw")
        self.client.force_authenticate(user=other)
        url = f"/api/trail/{marker.id}/"
        resp = self.client.patch(url, {"user_note": "x"}, format="json")
        self.assertEqual(resp.status_code, 403)
