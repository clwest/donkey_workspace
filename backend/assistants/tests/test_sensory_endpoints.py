from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, HapticFeedbackChannel, AssistantSensoryExtensionProfile


class SensoryEndpointsTest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="Touch", specialty="s")

    def test_codex_voice_command(self):
        url = "/api/assistants/codex/voice/"
        resp = self.client.post(url, {"transcript": "invoke ritual"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["action"], "invoke_ritual")

    def test_assistant_sensory_profile(self):
        url = f"/api/assistants/{self.assistant.id}/sensory/"
        resp = self.client.post(
            url,
            {
                "supported_modes": ["haptic"],
                "feedback_triggers": {"edit": "vibrate"},
                "memory_response_style": "warm",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        profile = AssistantSensoryExtensionProfile.objects.get(assistant=self.assistant)
        self.assertIn("haptic", profile.supported_modes)

    def test_haptic_ritual(self):
        url = "/api/assistants/rituals/haptic/"
        resp = self.client.post(
            url,
            {
                "assistant_id": str(self.assistant.id),
                "feedback_name": "tremor",
                "trigger_event": "codex edit",
                "intensity_level": 0.8,
                "symbolic_context": "edit complete",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(HapticFeedbackChannel.objects.filter(linked_assistant=self.assistant).count(), 1)

