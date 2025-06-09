import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from assistants.models import Assistant
from assistants.models.reflection import AssistantReflectionLog
from assistants.models.assistant import AssistantDriftRefinementLog
from memory.models import MemoryEntry
from assistants.utils.trust_profile import compute_trust_score

from django.test import TestCase


class ComputeTrustScoreTest(TestCase):
    def test_score_levels(self):
        a = Assistant.objects.create(name="A", slug="a", glossary_score=80)
        MemoryEntry.objects.create(assistant=a, event="m")
        for i in range(3):
            AssistantReflectionLog.objects.create(assistant=a, title=f"r{i}", summary="s")
        score = compute_trust_score(a)
        self.assertEqual(score["level"], "ready")
        self.assertGreaterEqual(score["score"], 80)

    def test_low_score(self):
        a = Assistant.objects.create(name="B", slug="b", glossary_score=10)
        AssistantDriftRefinementLog.objects.create(assistant=a)
        out = compute_trust_score(a)
        self.assertEqual(out["level"], "needs_attention")
        self.assertLess(out["score"], 50)
