import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.core.cache import cache
from django.contrib.auth import get_user_model
from mcp_core.models import NarrativeThread, MemoryContext
from mcp_core.views.threading import thread_summary

class PaginationTest(APITestCase):
    def setUp(self):
        for i in range(30):
            MemoryContext.objects.create(content=f"m{i}")

    def test_memory_list_pagination(self):
        resp = self.client.get("/api/mcp/memories/?page=2&page_size=10")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("results", resp.json())
        self.assertEqual(len(resp.json()["results"]), 10)

class CacheTest(APITestCase):
    def setUp(self):
        self.thread = NarrativeThread.objects.create(title="C")
        MemoryContext.objects.create(content="a", thread=self.thread)

    def test_thread_summary_cached(self):
        key = f"thread_summary_{self.thread.id}"
        cache.delete(key)
        url = f"/api/mcp/threads/{self.thread.id}/summary/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(cache.get(key))

class ThrottleTest(APITestCase):
    def test_prompt_usage_throttle(self):
        User = get_user_model()
        user = User.objects.create_user(username="u", password="p")
        self.client.force_authenticate(user=user)
        payload = {
            "prompt_slug": "s",
            "prompt_title": "t",
            "rendered_prompt": "x",
            "used_by": "test",
        }
        url = "/api/mcp/prompt-usage/"
        for _ in range(5):
            resp = self.client.post(url, payload)
            self.assertIn(resp.status_code, [201, 429])
        resp = self.client.post(url, payload)
        self.assertEqual(resp.status_code, 429)
