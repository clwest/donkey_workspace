import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from unittest.mock import patch
from assistants.models import AssistantCommandLog

class CLICommandAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="cliuser", password="pw", is_staff=True)
        self.client.force_authenticate(user=self.user)

    @patch("devtools.tasks.subprocess.Popen")
    def test_run_cli_command(self, mock_popen):
        proc = mock_popen.return_value
        proc.communicate.return_value = ("done", "")
        proc.returncode = 0
        resp = self.client.post("/api/dev/cli/run/", {"command": "show_urls"}, format="json")
        self.assertEqual(resp.status_code, 200)
        log_id = resp.json()["log_id"]
        log = AssistantCommandLog.objects.get(id=log_id)
        self.assertEqual(log.status, "success")
        self.assertIn("done", log.output)
        resp = self.client.get(f"/api/dev/command-logs/{log_id}/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")

    def test_list_cli_commands(self):
        resp = self.client.get("/api/dev/cli/list/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("results", data)
        self.assertTrue(any(cmd["name"] == "show_urls" for cmd in data["results"]))
