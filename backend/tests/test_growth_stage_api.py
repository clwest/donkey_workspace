import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant


class GrowthStageAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()

    def test_no_upgrade_without_points(self):
        assistant = Assistant.objects.create(name="Grow", specialty="demo", created_by=self.user)
        url = f"/api/assistants/{assistant.slug}/growth_stage/upgrade/"
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        assistant.refresh_from_db()
        self.assertEqual(assistant.growth_stage, 0)

    def test_upgrade_when_threshold_met(self):
        assistant = Assistant.objects.create(
            name="Grow2",
            specialty="demo",
            created_by=self.user,
            growth_points=10,
        )
        url = f"/api/assistants/{assistant.slug}/growth_stage/upgrade/"
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        assistant.refresh_from_db()
        self.assertEqual(assistant.growth_stage, 1)

    def test_upgrade_logs_reflection(self):
        assistant = Assistant.objects.create(
            name="Grow3",
            specialty="demo",
            created_by=self.user,
            growth_points=10,
        )
        url = f"/api/assistants/{assistant.slug}/growth_stage/upgrade/"
        self.client.post(url)
        from assistants.models.reflection import AssistantReflectionLog

        self.assertTrue(
            AssistantReflectionLog.objects.filter(
                assistant=assistant, title__icontains="Stage"
            ).exists()
        )
