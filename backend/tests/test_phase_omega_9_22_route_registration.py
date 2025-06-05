import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from unittest.mock import patch
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, DelegationEvent, AssistantThoughtLog


class RouteRegistrationTest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.parent = Assistant.objects.create(name="P", slug="p")
        self.child = Assistant.objects.create(name="C", slug="c")
        self.event = DelegationEvent.objects.create(
            parent_assistant=self.parent,
            child_assistant=self.child,
            reason="r",
        )
        AssistantThoughtLog.objects.create(
            assistant=self.child,
            thought="out",
            thought_type="generated",
        )

    def _find_route(self, data, keyword):
        for r in data:
            if keyword in r.get("path", ""):
                return r
        return None

    def test_routes_registered_and_tagged(self):
        resp = self.client.get("/api/dev/routes/fullmap/")
        self.assertEqual(resp.status_code, 200)
        routes = resp.json().get("routes", [])
        for kw in ["summarize_delegations", "reflect_on_self", "subagent_reflect"]:
            entry = self._find_route(routes, kw)
            self.assertIsNotNone(entry, f"Missing route for {kw}")
            self.assertTrue(entry.get("capability"), f"Route {kw} missing capability tag")

    @patch("assistants.utils.delegation_summary_engine.call_llm", return_value="ok")
    def test_summarize_delegations_endpoint(self, mock_llm):
        url = f"/api/assistants/{self.parent.slug}/summarize_delegations/"
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)

    @patch("assistants.views.reflection.AssistantReflectionEngine.generate_reflection", return_value="done")
    def test_reflect_on_self_endpoint(self, mock_gen):
        url = f"/api/assistants/{self.parent.slug}/reflect_on_self/"
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)

    def test_subagent_reflect_endpoint(self):
        url = f"/api/assistants/{self.parent.slug}/subagent_reflect/{self.event.id}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
