
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, SpecializationDriftLog


class RecoveryEndpointTest(BaseAPITestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="RecBot", specialty="x")
        SpecializationDriftLog.objects.create(
            assistant=self.assistant,
            drift_score=0.9,
            summary="high drift",
            trigger_type="auto",
            auto_flagged=True,
            requires_retraining=True,
        )
        self.assistant.needs_recovery = True
        self.assistant.save()

    def test_recover_endpoint(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/recover/"
        resp = self.client.post(url, {}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assistant.refresh_from_db()
        self.assertFalse(self.assistant.needs_recovery)
        self.assertIn("summary", resp.data)

