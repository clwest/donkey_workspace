import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.test_settings')
import django

django.setup()

from django.test import TestCase
from memory.models import SymbolicMemoryAnchor

class SymbolicAnchorListAPITests(TestCase):
    def setUp(self):
        self.a1 = SymbolicMemoryAnchor.objects.create(slug='alpha', label='Alpha', fallback_score=1.0)
        self.a2 = SymbolicMemoryAnchor.objects.create(slug='clarity', label='Clarity', fallback_score=5.0)

    def test_search_and_order(self):
        resp = self.client.get('/api/memory/glossary/anchors/', {'q': 'clar'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()['results']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['label'], 'Clarity')

        resp = self.client.get('/api/memory/glossary/anchors/', {'order_by': '-fallback_score'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()['results']
        self.assertEqual(data[0]['label'], 'Clarity')
