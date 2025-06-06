import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor, AnchorReinforcementLog
from memory.services.reinforcement import reinforce_glossary_anchor


class AnchorReinforcementTests(TestCase):
    def test_accept_mutation_creates_reinforcement(self):
        assistant = Assistant.objects.create(name="A", specialty="s")
        anchor = SymbolicMemoryAnchor.objects.create(
            slug="zk", label="zk", suggested_label="zk rollup", assistant=assistant
        )
        client = APIClient()
        resp = client.post(f"/api/glossary/mutations/{anchor.id}/accept")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(AnchorReinforcementLog.objects.count(), 1)
        log = AnchorReinforcementLog.objects.first()
        self.assertEqual(log.anchor, anchor)
        self.assertIsNotNone(log.memory)
        self.assertTrue(log.memory.tags.filter(slug="reinforcement").exists())
        anchor.refresh_from_db()
        self.assertEqual(anchor.acquisition_stage, "reinforced")

    def test_reflection_reinforcement(self):
        assistant = Assistant.objects.create(name="B", specialty="s")
        anchor = SymbolicMemoryAnchor.objects.create(slug="evm", label="EVM")
        reinforce_glossary_anchor(anchor, assistant=assistant, source="reflection_boost", score=0.8)
        log = AnchorReinforcementLog.objects.first()
        self.assertIsNotNone(log)
        self.assertEqual(log.reason, "reflection_boost")
        self.assertEqual(log.memory.anchor, anchor)
        anchor.refresh_from_db()
        self.assertEqual(anchor.acquisition_stage, "reinforced")
