import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

from agents.models.core import Agent
from intel_core.models import Document
from images.models import SourceImage
from accounts.models import UserInteractionSummary


class AccountsAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="apiuser", password="pw")
        self.client.force_authenticate(user=self.user)

        # personal assistant created via signal
        self.assistant = self.user.personal_assistant

        self.agent = Agent.objects.create(
            name="Agent1",
            slug="agent1",
            parent_assistant=self.assistant,
        )

        self.document = Document.objects.create(
            user=self.user,
            title="Doc1",
            content="hello world",
            source_type="text",
        )

        self.image = SourceImage.objects.create(
            user=self.user,
            image_file=SimpleUploadedFile(
                "img.jpg", b"filecontent", content_type="image/jpeg"
            ),
            title="Img1",
        )

        self.summary = UserInteractionSummary.objects.create(
            user=self.user,
            period_start=timezone.now(),
            period_end=timezone.now(),
            message_count=3,
            average_sentiment=0.7,
            interaction_summary="Good",
        )

    def test_me_assistant(self):
        resp = self.client.get("/api/users/me/assistant/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data["id"], str(self.assistant.id))

    def test_me_agents(self):
        resp = self.client.get("/api/users/me/agents/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], str(self.agent.id))

    def test_me_documents(self):
        resp = self.client.get("/api/users/me/documents/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Doc1")

    def test_me_images(self):
        resp = self.client.get("/api/users/me/images/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Img1")

    def test_me_summary(self):
        resp = self.client.get("/api/users/me/summary/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertEqual(data["message_count"], 3)
        self.assertEqual(data["interaction_summary"], "Good")
