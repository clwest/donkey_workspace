from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, Badge
from assistants.utils.badge_logic import update_assistant_badges
from memory.models import SymbolicMemoryAnchor

class BadgeAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="Badge", specialty="t")
        Badge.objects.create(slug="glossary_apprentice", label="GA", criteria="acquired>=1")
        Badge.objects.create(slug="reflection_ready", label="RR", criteria="reflections>=1")

    def test_list_badges_with_assistant(self):
        SymbolicMemoryAnchor.objects.create(slug="t1", label="T1", assistant=self.assistant)
        update_assistant_badges(self.assistant)
        resp = self.client.get(f"/api/v1/badges/?assistant={self.assistant.slug}")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 2)
        ga = next(b for b in data if b["slug"] == "glossary_apprentice")
        self.assertTrue(ga["earned"])
        self.assertIsNotNone(ga["earned_at"])
        rr = next(b for b in data if b["slug"] == "reflection_ready")
        self.assertFalse(rr["earned"])

    def test_badge_progress_endpoint(self):
        resp = self.client.get(f"/api/v1/assistants/{self.assistant.slug}/badge_progress/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["assistant"], self.assistant.slug)
        self.assertIn("badges", data)
