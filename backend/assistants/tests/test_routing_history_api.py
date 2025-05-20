import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from assistants.models import Assistant, RoutingSuggestionLog


class RoutingHistoryAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="router", password="pw")
        self.client.force_authenticate(user=self.user)
        self.a1 = Assistant.objects.create(name="A1", specialty="root")
        self.a2 = Assistant.objects.create(name="A2", specialty="helper")
        for i in range(10):
            log = RoutingSuggestionLog.objects.create(
                context_summary=f"c{i}",
                suggested_assistant=self.a2,
                confidence_score=0.5 + i,
            )
            RoutingSuggestionLog.objects.filter(id=log.id).update(
                timestamp=timezone.now() + timezone.timedelta(minutes=i)
            )
        self.url = "/api/assistants/routing-history/"

    def test_list_history(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["results"]
        self.assertEqual(len(data), 10)
        self.assertEqual(data[0]["assistant_slug"], self.a2.slug)

    def test_filter_by_assistant(self):
        resp = self.client.get(self.url + f"?assistant={self.a2.slug}")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["results"]
        self.assertTrue(all(d["assistant_slug"] == self.a2.slug for d in data))
