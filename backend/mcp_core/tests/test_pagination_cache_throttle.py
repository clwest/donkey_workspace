import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import override_settings
from rest_framework.test import APITestCase
from django.conf import settings as django_settings
from mcp_core.models import NarrativeThread
from assistants.models import AssistantReflectionLog
from django.core.cache import cache

class PaginationTest(APITestCase):
    def setUp(self):
        for i in range(5):
            AssistantReflectionLog.objects.create(title=f"r{i}", summary="s")

    def test_reflection_list_pagination(self):
        resp = self.client.get("/api/v1/reflections/?page_size=2")
        assert resp.status_code == 200
        assert len(resp.json()["results"]) == 2

class CacheInvalidationTest(APITestCase):
    def setUp(self):
        self.thread = NarrativeThread.objects.create(title="C")

    def test_thread_summary_cache_invalidation(self):
        url = f"/api/v1/threads/{self.thread.id}/summary/"
        self.client.get(url)
        self.thread.title = "New"
        self.thread.save()
        cache_key = f"thread_summary_{self.thread.id}"
        assert cache.get(cache_key) is None
        resp = self.client.get(url)
        assert resp.status_code == 200
        assert resp.json()["title"] == "New"

class ThrottleTest(APITestCase):
    @override_settings(REST_FRAMEWORK={**django_settings.REST_FRAMEWORK, "DEFAULT_THROTTLE_RATES": {"user": "1/min"}})
    def test_prompt_usage_throttled(self):
        data = {"used_by": "t", "rendered_prompt": "p"}
        self.client.post("/api/v1/prompt-usage/", data)
        resp = self.client.post("/api/v1/prompt-usage/", data)
        assert resp.status_code == 429
