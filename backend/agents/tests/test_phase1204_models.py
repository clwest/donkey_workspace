import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    CodexLinkedGuild,
    MythCommunityCluster,
    SwarmFederationEngine,
)


class Phase1204ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="myth"
        )

    def test_codex_linked_guild(self):
        guild = CodexLinkedGuild.objects.create(
            guild_name="G",
            anchor_codex=self.codex,
            member_users=[],
            ritual_focus={},
            codex_compliance_score=0.9,
        )
        guild.member_assistants.add(self.assistant)
        self.assertEqual(guild.anchor_codex, self.codex)
        self.assertEqual(guild.member_assistants.count(), 1)

    def test_myth_community_cluster(self):
        cluster = MythCommunityCluster.objects.create(
            cluster_name="C",
            trait_map={},
            collective_memory_tags=[],
            participant_ids=[],
            shared_archetype_signature={},
        )
        self.assertEqual(cluster.cluster_name, "C")

    def test_swarm_federation_engine(self):
        guild = CodexLinkedGuild.objects.create(
            guild_name="G2",
            anchor_codex=self.codex,
            member_users=[],
            ritual_focus={},
            codex_compliance_score=0.7,
        )
        engine = SwarmFederationEngine.objects.create(
            symbolic_state_map={},
            federation_log="log",
            ritual_convergence_score=0.5,
        )
        engine.active_guilds.add(guild)
        self.assertEqual(engine.active_guilds.count(), 1)
