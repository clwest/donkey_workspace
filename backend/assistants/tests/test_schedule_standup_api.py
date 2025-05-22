
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant


class StandupScheduleAPITest(BaseAPITestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Parent", specialty="p")
        self.url = f"/api/v1/assistants/{self.assistant.id}/schedule-standup/"

    def test_schedule_standup(self):
        resp = self.client.post(self.url, {"time": "08:00"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "scheduled")
