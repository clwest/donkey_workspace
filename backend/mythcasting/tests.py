import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import CinemythStoryline, MythcastingChannel


class MythcastingChannelAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="user", password="pw")
        self.client.force_authenticate(user=self.user)
        self.storyline = CinemythStoryline.objects.create(title="S")

    def test_create_channel(self):
        resp = self.client.post(
            "/api/mythcasting/channels/",
            {
                "channel_name": "main",
                "active_storyline": str(self.storyline.id),
                "viewing_audience": [],
                "symbolic_broadcast_tags": [],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(MythcastingChannel.objects.count(), 1)
