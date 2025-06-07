import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.test_settings')
import django
django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from assistants.models import Assistant
from assistants.models.reflection import AssistantReflectionLog
from memory.models import ReflectionReplayLog, SymbolicMemoryAnchor

class DriftHeatmapEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.assistant = Assistant.objects.create(name='Heat', slug='heat')
        self.other = Assistant.objects.create(name='Other', slug='other')
        anchor = SymbolicMemoryAnchor.objects.create(slug='t', label='T')
        r1 = AssistantReflectionLog.objects.create(assistant=self.assistant, summary='a', title='a')
        ReflectionReplayLog.objects.create(
            original_reflection=r1,
            assistant=self.assistant,
            old_score=0.2,
            new_score=0.8,
            changed_anchors=['t'],
            replayed_summary='b',
        )
        r2 = AssistantReflectionLog.objects.create(assistant=self.other, summary='b', title='b')
        ReflectionReplayLog.objects.create(
            original_reflection=r2,
            assistant=self.other,
            old_score=0.1,
            new_score=0.9,
            changed_anchors=['t'],
            replayed_summary='c',
        )

    def test_heatmap_filters_by_assistant(self):
        resp = self.client.get(f"/api/assistants/{self.assistant.slug}/drift_heatmap/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()['results']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['anchor_slug'], 't')
