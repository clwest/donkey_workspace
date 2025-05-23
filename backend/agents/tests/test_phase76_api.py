import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from agents.models import MythflowOrchestrationPlan


class Phase76APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")

    def test_create_mythflow_plan(self):
        resp = self.client.post(
            "/api/v1/agents/mythflow-plans/",
            {
                "title": "Plan",
                "lead_assistant": self.assistant.id,
                "goal_sequence": [],
                "narrative_constraints": "none",
                "participating_agents": [self.assistant.id],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/agents/mythflow-plans/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_directive_memory(self):
        resp = self.client.post(
            "/api/v1/agents/directive-memory/",
            {
                "assistant": self.assistant.id,
                "purpose_statement": "p",
                "triggering_conditions": {},
                "directive_tags": {},
                "temporal_scope": "all",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/agents/directive-memory/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_planning_lattice(self):
        plan = MythflowOrchestrationPlan.objects.create(
            title="Plan",
            lead_assistant=self.assistant,
            goal_sequence=[],
            narrative_constraints="x",
        )
        plan.participating_agents.add(self.assistant)
        resp = self.client.post(
            "/api/v1/agents/planning-lattices/",
            {
                "associated_plan": plan.id,
                "role_nodes": {},
                "narrative_edges": {},
                "alignment_scores": {},
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/agents/planning-lattices/")
        self.assertEqual(len(list_resp.json()), 1)
