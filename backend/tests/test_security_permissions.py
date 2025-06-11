import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant

class SecurityPermissionsTest(BaseAPITestCase):
    def setUp(self):
        self.user = self.authenticate()
        self.other = self.authenticate("other", "pw2")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A", slug="a", created_by=self.user)

    def test_protected_endpoint_requires_auth(self):
        self.client.force_authenticate(user=None)
        resp = self.client.get("/api/v1/assistants/")
        assert resp.status_code == 401

    def test_is_owner_or_admin(self):
        url = f"/api/assistants/{self.assistant.slug}/setup_summary/"
        self.client.force_authenticate(user=self.other)
        resp = self.client.get(url)
        assert resp.status_code in (403, 404)
