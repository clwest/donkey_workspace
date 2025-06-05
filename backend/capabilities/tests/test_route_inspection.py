import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from assistants.tests import BaseAPITestCase


class RouteInspectionTest(BaseAPITestCase):
    def test_full_route_map_metadata(self):
        resp = self.client.get("/api/dev/routes/fullmap/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json().get("routes", [])
        self.assertTrue(
            any(
                all(key in r for key in ["view", "module", "name", "capability"]) 
                for r in data
            )
        )
        paths = [r["path"] for r in data]
        for p in [
            "api/assistants/<slug:slug>/summarize_delegations/",
            "api/assistants/<slug:slug>/reflect_on_self/",
            "api/assistants/<slug:slug>/subagent_reflect/",
        ]:
            assert p in paths

    def test_capability_status_structure(self):
        resp = self.client.get("/api/capabilities/status/")
        self.assertEqual(resp.status_code, 200)
        caps = resp.json().get("capabilities", [])
        if caps:
            cap = caps[0]
            for field in ["capability", "route", "view", "status"]:
                self.assertIn(field, cap)

