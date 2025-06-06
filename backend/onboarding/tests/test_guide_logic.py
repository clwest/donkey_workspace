import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from onboarding.guide_logic import suggest_next_hint
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor
from memory.services.acquisition import update_anchor_acquisition


class GuideLogicTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="logic", password="pw")
        self.assistant = Assistant.objects.create(
            name="L", slug="logic-a", created_by=self.user
        )

    def test_glossary_hint_suggested(self):
        hint, action = suggest_next_hint(self.user)
        self.assertEqual(hint, "glossary_tour")
        self.assertIn("/assistants/", action)

    def test_rag_hint_after_anchor(self):
        anchor = SymbolicMemoryAnchor.objects.create(
            slug="t", label="T", assistant=self.assistant
        )
        update_anchor_acquisition(anchor, "acquired")
        hint, _ = suggest_next_hint(self.user)
        self.assertEqual(hint, "rag_intro")
