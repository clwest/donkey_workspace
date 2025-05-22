
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase

from assistants.models import Assistant, AssistantMythLayer
from agents.models import GlobalMissionNode
from assistants.utils.cross_canon_prediction import predict_cross_canon_outcomes


class MythLayerJournalTest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Mythic", specialty="magic")

    def test_create_and_get_myth_layer(self):
        url = f"/api/assistants/{self.assistant.slug}/myth-layer/"
        resp = self.client.post(
            url,
            {"origin_story": "Born", "legendary_traits": {"epithet": "Hero"}},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["legendary_traits"]["epithet"], "Hero")

    def test_prediction_returns_dict(self):
        node = GlobalMissionNode.objects.create(title="Root", description="d")
        result = predict_cross_canon_outcomes(node)
        self.assertIsInstance(result, dict)

