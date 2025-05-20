import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from assistants.models import Assistant, AssistantSkill


class AssistantSkillsAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="skill", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Skiller", specialty="plan")

    def test_get_and_create_skills(self):
        url = f"/api/assistants/{self.assistant.slug}/skills/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])

        resp = self.client.post(url, {"name": "planning", "confidence": 0.8})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(AssistantSkill.objects.count(), 1)
        skill = AssistantSkill.objects.first()
        self.assertEqual(skill.name, "planning")

        resp = self.client.get(url)
        self.assertEqual(len(resp.json()), 1)
