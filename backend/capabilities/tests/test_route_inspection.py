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
        self.assertTrue(any("view" in r and "module" in r for r in data))

    def test_capability_status_structure(self):
        resp = self.client.get("/api/capabilities/status/")
        self.assertEqual(resp.status_code, 200)
        caps = resp.json().get("capabilities", [])
        if caps:
            cap = caps[0]
            for field in ["capability", "route", "view", "status"]:
                self.assertIn(field, cap)

