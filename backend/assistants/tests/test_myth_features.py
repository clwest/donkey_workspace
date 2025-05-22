
from django.test import TestCase
from django.contrib.auth import get_user_model

from assistants.models import Assistant
from agents.models import LoreEntry, SwarmMemoryEntry
from assistants.utils.mythology import score_symbolic_convergence, trigger_metamorphosis


class MythFeatureTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="myther", password="pw")
        self.assistant = Assistant.objects.create(
            name="Mythic", specialty="symbols", created_by=self.user
        )
        self.lore = LoreEntry.objects.create(
            title="Guardian Legend", summary="mythic guardian synergy"
        )

    def test_symbolic_convergence_score_range(self):
        score = score_symbolic_convergence(self.assistant, self.lore)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_trigger_metamorphosis_creates_memory(self):
        result = trigger_metamorphosis(self.assistant)
        self.assistant.refresh_from_db()
        self.assertIn("Awakened", self.assistant.name)
        self.assertTrue(SwarmMemoryEntry.objects.filter(id=result["memory_entry"]).exists())
