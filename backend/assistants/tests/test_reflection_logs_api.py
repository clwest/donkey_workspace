import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase

from assistants.models import Assistant, AssistantProject, AssistantReflectionLog

class AssistantReflectionLogAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="viewer", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Tester", specialty="test")
        self.project = AssistantProject.objects.create(
            assistant=self.assistant, title="Proj", created_by=self.user
        )
        r1 = AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            project=self.project,
            summary="first",
            title="R1",
        )
        r2 = AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            project=self.project,
            summary="second",
            title="R2",
        )
        # ensure ordering
        AssistantReflectionLog.objects.filter(id=r1.id).update(
            created_at=timezone.now() - timedelta(minutes=1)
        )
        AssistantReflectionLog.objects.filter(id=r2.id).update(
            created_at=timezone.now()
        )
        self.ref1 = AssistantReflectionLog.objects.get(id=r1.id)
        self.ref2 = AssistantReflectionLog.objects.get(id=r2.id)

    def test_list_reflections_for_assistant(self):
        url = f"/api/assistants/{self.assistant.slug}/reflections/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 2)
        self.assertGreater(data[0]["created_at"], data[1]["created_at"])
        expected = {"id", "created_at", "project", "summary", "linked_memory", "tags"}
        self.assertTrue(expected.issubset(set(data[0].keys())))

    def test_reflection_detail(self):
        url = f"/api/assistants/reflections/{self.ref1.id}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        expected = {
            "id",
            "summary",
            "raw_summary",
            "raw_prompt",
            "llm_summary",
            "linked_memory",
            "tags",
            "created_at",
        }
        self.assertTrue(expected.issubset(set(data.keys())))

