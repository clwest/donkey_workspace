import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

import json
from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from assistants.models import Assistant


class RunRagTestsSlugId(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A", slug="runner")

    def _run(self, ident):
        tmp = StringIO()
        path = "tmp_empty.json"
        with open(path, "w") as f:
            json.dump({"tests": []}, f)
        call_command("run_rag_tests", "--assistant", ident, "--file", path, stdout=tmp)
        return tmp.getvalue()

    def test_slug_and_id(self):
        out1 = self._run(self.assistant.slug)
        self.assertIn("0/0", out1)
        out2 = self._run(str(self.assistant.id))
        self.assertIn("0/0", out2)
