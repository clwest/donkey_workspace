import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    TranscendentMyth,
    MemoryRealmZone,
    MythHyperstructure,
    DreamWorldModel,
    ReflectiveEcosystemEngine,
)


class Phase90BModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Alpha")
        self.codex = SwarmCodex.objects.create(title="C", created_by=self.assistant)
        self.myth = TranscendentMyth.objects.create(name="Myth")
        self.zone = MemoryRealmZone.objects.create(
            zone_name="Z",
            origin_myth=self.myth,
            spatial_traits={},
            symbolic_navigation_tags={},
        )

    def test_myth_hyperstructure(self):
        hs = MythHyperstructure.objects.create(
            structure_name="Temple",
            symbolic_geometry="geom",
            purpose_vector_map={},
        )
        hs.linked_codices.add(self.codex)
        hs.assistants_inhabiting.add(self.assistant)
        self.assertEqual(hs.structure_name, "Temple")
        self.assertIn(self.codex, hs.linked_codices.all())

    def test_dream_world_model(self):
        world = DreamWorldModel.objects.create(
            world_name="Dream",
            myth_source=self.myth,
            simulation_state={},
        )
        world.memory_zones.add(self.zone)
        world.active_agents.add(self.assistant)
        self.assertEqual(world.world_name, "Dream")
        self.assertIn(self.zone, world.memory_zones.all())

    def test_reflective_ecosystem_engine(self):
        engine = ReflectiveEcosystemEngine.objects.create(
            scope="guild",
            symbolic_flux_data={},
            entropy_modulators={},
            ritual_activity_log={},
        )
        self.assertEqual(engine.scope, "guild")
