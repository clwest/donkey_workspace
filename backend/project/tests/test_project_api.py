import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from project.models import Project


class ProjectAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="owner", password="pw")
        self.other = User.objects.create_user(username="other", password="pw")
        self.client.force_authenticate(user=self.user)

    def test_project_crud_and_slug_uniqueness(self):
        resp1 = self.client.post(
            "/api/v1/projects/", {"title": "My Project"}, format="json"
        )
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)
        project_id = resp1.json()["id"]
        slug1 = resp1.json()["slug"]

        resp2 = self.client.post(
            "/api/v1/projects/", {"title": "My Project"}, format="json"
        )
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)
        slug2 = resp2.json()["slug"]
        self.assertNotEqual(slug1, slug2)

        resp = self.client.get(f"/api/v1/projects/{project_id}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()["title"], "My Project")

        resp = self.client.patch(
            f"/api/v1/projects/{project_id}/",
            {"title": "Updated"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(Project.objects.get(id=project_id).title, "Updated")

        resp = self.client.delete(f"/api/v1/projects/{project_id}/")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(id=project_id).exists())

    def test_unauthorized_access_forbidden(self):
        project = Project.objects.create(user=self.user, title="Secret")
        url = f"/api/v1/projects/{project.id}/"

        self.client.force_authenticate(user=self.other)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        resp = self.client.patch(url, {"title": "x"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

