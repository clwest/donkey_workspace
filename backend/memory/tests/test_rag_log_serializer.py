import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from memory.models import RAGGroundingLog
from memory.serializers import RAGGroundingLogSerializer

class RagGroundingLogSerializerTest(TestCase):
    def test_serializer_includes_hits(self):
        a = Assistant.objects.create(name="A", specialty="s")
        log = RAGGroundingLog.objects.create(
            assistant=a,
            query="q",
            used_chunk_ids=["1"],
            fallback_triggered=False,
            glossary_hits=["term"],
            glossary_misses=[],
            retrieval_score=0.5,
            expected_anchor="term",
            raw_score=0.4,
            adjusted_score=0.6,
            glossary_boost_applied=0.2,
            boosted_from_reflection=False,
            reflection_boost_score=0.0,
            glossary_boost_type="chunk",
            fallback_threshold_used=0.6,
        )
        data = RAGGroundingLogSerializer(log).data
        self.assertEqual(data["glossary_hits"], ["term"])
        self.assertIn("corrected_score", data)
        self.assertEqual(data["expected_anchor"], "term")
        self.assertIn("raw_score", data)
        self.assertEqual(data["adjusted_score"], 0.6)

