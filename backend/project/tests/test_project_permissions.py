import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from project.models import Project


class ProjectPermissionsTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(username="owner", password="pw")
        self.other = User.objects.create_user(username="other", password="pw")
        self.project = Project.objects.create(user=self.owner, title="Hidden")

    def test_other_user_cannot_view_project(self):
        self.client.force_authenticate(user=self.other)
        url = f"/api/projects/{self.project.id}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_other_user_cannot_update_project(self):
        self.client.force_authenticate(user=self.other)
        url = f"/api/projects/{self.project.id}/"
        resp = self.client.patch(url, {"title": "New"}, format="json")
        self.assertEqual(resp.status_code, 403)
