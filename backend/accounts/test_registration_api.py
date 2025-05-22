import os

# Ensure Django settings are configured for tests
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from assistants.models import AssistantProject
from project.models import Project


class RegistrationSignalAPITest(APITestCase):
    def test_registration_creates_assistant_and_project(self):
        url = "/api/dj-rest-auth/registration/"
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "strong-pass",
            "password2": "strong-pass",
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 201)

        User = get_user_model()
        user = User.objects.get(username="newuser")
        self.assertIsNotNone(user.personal_assistant)

        assistant = user.personal_assistant
        self.assertTrue(
            AssistantProject.objects.filter(
                assistant=assistant, created_by=user
            ).exists()
        )
        self.assertTrue(Project.objects.filter(user=user, assistant=assistant).exists())
