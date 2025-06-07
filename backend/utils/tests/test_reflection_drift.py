import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.test_settings')
import django
django.setup()

from django.test import TestCase
from assistants.models import Assistant
from assistants.models.reflection import AssistantReflectionLog
from memory.models import ReflectionReplayLog, SymbolicMemoryAnchor
from utils.reflection_drift import aggregate_drift_by_anchor

class ReflectionDriftAggregationTests(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name='A')
        self.anchor = SymbolicMemoryAnchor.objects.create(slug='term', label='Term')
        self.reflection = AssistantReflectionLog.objects.create(
            assistant=self.assistant, summary='t', title='T'
        )
        ReflectionReplayLog.objects.create(
            original_reflection=self.reflection,
            assistant=self.assistant,
            old_score=0.1,
            new_score=0.9,
            changed_anchors=[self.anchor.slug],
            replayed_summary='better',
        )

    def test_aggregate(self):
        results = aggregate_drift_by_anchor(self.assistant)
        self.assertEqual(len(results), 1)
        row = results[0]
        self.assertEqual(row['anchor_slug'], 'term')
        self.assertEqual(row['frequency'], 1)
        self.assertAlmostEqual(row['avg_drift_score'], 0.8, places=2)
