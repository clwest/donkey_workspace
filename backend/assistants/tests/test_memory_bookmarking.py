
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase

from assistants.models import Assistant
from assistants.helpers.logging_helper import log_assistant_thought
from memory.models import MemoryEntry


class MemoryBookmarkingTest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Booker", specialty="s")

    def test_bookmark_toggle_idempotent(self):
        mem = MemoryEntry.objects.create(event="x", assistant=self.assistant)
        url = f"/api/v1/memory/{mem.id}/bookmark/"

        resp = self.client.post(url, {"label": "Important"}, format="json")
        self.assertEqual(resp.status_code, 200)
        mem.refresh_from_db()
        self.assertTrue(mem.is_bookmarked)
        self.assertEqual(mem.bookmark_label, "Important")

        resp = self.client.post(url, {"label": "Important"}, format="json")
        self.assertEqual(resp.status_code, 200)
        mem.refresh_from_db()
        self.assertTrue(mem.is_bookmarked)
        self.assertEqual(mem.bookmark_label, "Important")

        resp = self.client.post(f"/api/v1/memory/{mem.id}/unbookmark/", format="json")
        self.assertEqual(resp.status_code, 200)
        mem.refresh_from_db()
        self.assertFalse(mem.is_bookmarked)
        self.assertIsNone(mem.bookmark_label)

    def test_bookmarked_filter_and_label_search(self):
        m1 = MemoryEntry.objects.create(event="one", assistant=self.assistant)
        m2 = MemoryEntry.objects.create(event="two", assistant=self.assistant)
        m3 = MemoryEntry.objects.create(event="three", assistant=self.assistant)

        self.client.post(
            f"/api/v1/memory/{m1.id}/bookmark/",
            {"label": "Goal change"},
            format="json",
        )
        self.client.post(
            f"/api/v1/memory/{m2.id}/bookmark/",
            {"label": "trigger memory"},
            format="json",
        )

        resp = self.client.get(
            f"/api/v1/memory/bookmarked/?assistant={self.assistant.slug}"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 2)

        resp = self.client.get("/api/v1/memory/bookmarked/?label=goal")
        labels = [d["bookmark_label"] for d in resp.json()]
        self.assertIn("Goal change", labels)
        self.assertNotIn("trigger memory", labels)

    def test_log_assistant_thought_auto_bookmark(self):
        mem = MemoryEntry.objects.create(event="auto", assistant=self.assistant)
        log_assistant_thought(
            self.assistant,
            "note",
            linked_memory=mem,
            bookmark_label="Trigger memory",
        )
        mem.refresh_from_db()
        self.assertTrue(mem.is_bookmarked)
        self.assertEqual(mem.bookmark_label, "Trigger memory")
