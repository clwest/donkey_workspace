from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, DemoUsageLog
from assistants.models.demo_usage import DemoSessionLog
from assistants.helpers.demo_utils import get_or_create_usage_for_session


class DemoUsageUtilsTest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.demo = Assistant.objects.create(
            name="Demo",
            slug="demo",
            demo_slug="demo",
            is_demo=True,
        )
        self.session_id = "sess1"
        DemoSessionLog.objects.create(assistant=self.demo, session_id=self.session_id)

    def test_get_or_create_usage_race_safe(self):
        usage1, created1 = get_or_create_usage_for_session(self.session_id)
        usage2, created2 = get_or_create_usage_for_session(self.session_id)
        self.assertEqual(usage1.id, usage2.id)
        self.assertTrue(created1)
        self.assertFalse(created2)
        self.assertEqual(DemoUsageLog.objects.filter(session_id=self.session_id).count(), 1)

