
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from assistants.models import Assistant, DelegationEvent, DelegationStrategy
from assistants.utils.recommendation_engine import suggest_agent_for_task
from memory.models import MemoryEntry
from mcp_core.models import Tag


class DelegationStrategyRecommendationTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="rec", password="pw")
        self.parent = Assistant.objects.create(name="Parent", specialty="general")
        self.specialist = Assistant.objects.create(name="Spec", specialty="tts")
        self.other = Assistant.objects.create(name="Other", specialty="other")
        self.memory = MemoryEntry.objects.create(event="m", assistant=self.parent)
        tag = Tag.objects.create(name="tts", slug="tts")
        self.memory.tags.add(tag)
        DelegationEvent.objects.create(
            parent_assistant=self.parent,
            child_assistant=self.specialist,
            score=5,
        )
        DelegationStrategy.objects.create(assistant=self.parent)

    def test_trusted_specialist_preferred(self):
        res = suggest_agent_for_task(self.parent, self.memory)
        self.assertIsNotNone(res)
        self.assertEqual(res["assistant_id"], str(self.specialist.id))

    def test_avoid_recent_failures(self):
        week_ago = timezone.now() - timezone.timedelta(hours=1)
        for _ in range(3):
            DelegationEvent.objects.create(
                parent_assistant=self.parent,
                child_assistant=self.other,
                score=1,
                created_at=week_ago,
            )
        res = suggest_agent_for_task(self.parent, self.memory)
        self.assertEqual(res["assistant_id"], str(self.specialist.id))

    def test_avoid_active_threshold(self):
        strategy = self.parent.delegation_strategy
        strategy.max_active_delegations = 2
        strategy.save()
        for _ in range(3):
            DelegationEvent.objects.create(
                parent_assistant=self.parent,
                child_assistant=self.specialist,
            )
        res = suggest_agent_for_task(self.parent, self.memory)
        self.assertEqual(res["assistant_id"], str(self.other.id))

    def test_fallback_when_no_match(self):
        self.memory.tags.clear()
        res = suggest_agent_for_task(self.parent, self.memory)
        self.assertIsNotNone(res)
        # highest trust agent chosen when no tag match
        self.assertEqual(res["assistant_id"], str(self.specialist.id))

