import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    MythflowOrchestrationPlan,
    DirectiveMemoryNode,
    SymbolicPlanningLattice,
)


class Phase76ModelsTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Alpha")
        self.plan = MythflowOrchestrationPlan.objects.create(
            title="Plan",
            lead_assistant=self.assistant,
            goal_sequence=[],
            narrative_constraints="n",
        )
        self.plan.participating_agents.add(self.assistant)

    def test_directive_memory_node(self):
        node = DirectiveMemoryNode.objects.create(
            assistant=self.assistant,
            purpose_statement="p",
            triggering_conditions={},
            directive_tags={},
            temporal_scope="all",
        )
        self.assertEqual(node.assistant, self.assistant)

    def test_planning_lattice_creation(self):
        lattice = SymbolicPlanningLattice.objects.create(
            associated_plan=self.plan,
            role_nodes={},
            narrative_edges={},
            alignment_scores={},
        )
        self.assertEqual(lattice.associated_plan, self.plan)
