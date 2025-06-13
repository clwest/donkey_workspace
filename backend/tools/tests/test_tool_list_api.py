import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from tools.models import Tool


class ToolListAPITest(APITestCase):
    def setUp(self):
        Tool.objects.create(
            name="A", slug="a", module_path="x", function_name="f"
        )
        Tool.objects.create(
            name="B", slug="b", module_path="x", function_name="g", is_active=False
        )

    def test_list_only_active(self):
        resp = self.client.get("/api/tools/")
        self.assertEqual(resp.status_code, 200)
        slugs = {t["slug"] for t in resp.json()}
        self.assertIn("a", slugs)
        self.assertNotIn("b", slugs)
