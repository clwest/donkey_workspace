import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.models.reflection import AssistantReflectionLog
from assistants.models.assistant import AssistantDriftRefinementLog
from memory.models import MemoryEntry, RAGGroundingLog


class AssistantTrustProfileAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()

    def test_trust_profile_endpoint(self):
        a = Assistant.objects.create(name="T", slug="t", glossary_score=0.6)
        MemoryEntry.objects.create(assistant=a, event="m1")
        AssistantReflectionLog.objects.create(assistant=a, title="r1", summary="s")
        AssistantDriftRefinementLog.objects.create(assistant=a)
        RAGGroundingLog.objects.create(
            assistant=a,
            query="q",
            glossary_hits=["a"],
            glossary_misses=[],
            used_chunk_ids=[],
        )
        a.skill_badges = ["one", "two"]
        a.save()

        url = f"/api/assistants/{a.slug}/trust_profile/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("trust_score", data)
        self.assertIn("trust_level", data)
        self.assertEqual(data["earned_badge_count"], 2)
        self.assertEqual(data["reflections_last_7d"], 1)
        self.assertEqual(data["drift_fix_count"], 1)
        self.assertAlmostEqual(data["glossary_hit_ratio"], 1.0)
