import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from agents.models import Agent, AgentSkill, AgentSkillLink, AgentLegacy, AgentCluster, SwarmMemoryEntry
from agents.utils.agent_controller import resurrect_legacy_agent


class LegacyResurrectionTest(TestCase):
    def setUp(self):
        self.agent = Agent.objects.create(name="Old", slug="old", tags=["t"], skills=["s"], specialty="s")
        self.skill = AgentSkill.objects.create(name="s")
        AgentSkillLink.objects.create(agent=self.agent, skill=self.skill, source="orig")
        self.cluster = AgentCluster.objects.create(name="c1")
        self.cluster.agents.add(self.agent)
        self.legacy = AgentLegacy.objects.get(agent=self.agent)

    def test_resurrect_legacy_agent(self):
        new_agent = resurrect_legacy_agent(self.legacy, "need")
        self.assertNotEqual(new_agent.id, self.agent.id)
        self.assertEqual(list(new_agent.tags), list(self.agent.tags))
        self.assertEqual(list(new_agent.skills), list(self.agent.skills))
        self.assertTrue(AgentSkillLink.objects.filter(agent=new_agent, skill=self.skill).exists())
        self.assertTrue(self.cluster.agents.filter(id=new_agent.id).exists())
        self.legacy.refresh_from_db()
        self.assertEqual(self.legacy.resurrection_count, 1)
        self.assertEqual(SwarmMemoryEntry.objects.count(), 1)
