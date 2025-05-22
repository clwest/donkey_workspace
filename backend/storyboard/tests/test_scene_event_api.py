import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta

from assistants.models import Assistant
from storyboard.models import NarrativeEvent


class SceneEventAPITest(APITestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(
            name="Scout",
            specialty="scouting",
            preferred_scene_tags=["temple", "lab"],
        )
        self.url = f"/api/v1/storyboard/relevant/{self.assistant.slug}/"

    def test_relevant_endpoint(self):
        now = timezone.now()
        e1 = NarrativeEvent.objects.create(
            title="Temple Meeting",
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=2),
            scene="temple",
        )
        e2 = NarrativeEvent.objects.create(
            title="Generic",
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=2),
        )
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        titles = [e["title"] for e in resp.json()]
        self.assertEqual(titles[0], "Temple Meeting")
