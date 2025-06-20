import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from rest_framework.test import APITestCase

from assistants.models import Assistant, AssistantThoughtLog
from storyboard.models import NarrativeEvent
from storyboard.tasks import evaluate_narrative_triggers


class NarrativeTriggerTaskTest(APITestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(
            name="Main", specialty="root", preferred_scene_tags=["lab"]
        )

    @patch("storyboard.tasks.spawn_delegated_assistant")
    def test_auto_delegate_spawns_child(self, mock_spawn):
        NarrativeEvent.objects.create(
            title="Upcoming",
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=2),
            linked_assistant=self.assistant,
            auto_delegate=True,
            scene="lab",
        )

        evaluate_narrative_triggers()
        self.assertTrue(mock_spawn.called)

    @patch("storyboard.tasks.AssistantReflectionEngine")
    def test_auto_reflect_invoked(self, mock_engine):
        event = NarrativeEvent.objects.create(
            title="Ongoing",
            start_time=timezone.now() - timedelta(minutes=10),
            end_time=timezone.now() + timedelta(minutes=10),
            linked_assistant=self.assistant,
            auto_reflect=True,
        )

        evaluate_narrative_triggers()
        mock_engine.return_value.reflect_now.assert_called_once()
        event.refresh_from_db()
        self.assertIsNotNone(event.last_triggered)

    def test_auto_summarize_logs_thought(self):
        event = NarrativeEvent.objects.create(
            title="Ended",
            start_time=timezone.now() - timedelta(hours=2),
            end_time=timezone.now() - timedelta(hours=1),
            linked_assistant=self.assistant,
            auto_summarize=True,
        )

        evaluate_narrative_triggers()
        log = AssistantThoughtLog.objects.filter(linked_event=event).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.thought_type, "timeline_trigger")
        self.assertEqual(log.origin, "automatic")

    @patch("storyboard.tasks.spawn_delegated_assistant")
    def test_scene_match_triggers(self, mock_spawn):
        self.assistant.preferred_scene_tags = ["castle", "night"]
        self.assistant.save()

        NarrativeEvent.objects.create(
            title="Castle Raid",
            start_time=timezone.now() + timedelta(minutes=1),
            end_time=timezone.now() + timedelta(hours=1),
            linked_assistant=self.assistant,
            scene="castle",
        )
        NarrativeEvent.objects.create(
            title="Forest Walk",
            start_time=timezone.now() + timedelta(minutes=1),
            end_time=timezone.now() + timedelta(hours=1),
            scene="forest",
        )

        evaluate_narrative_triggers()
        mock_spawn.assert_called_once()
        thought = AssistantThoughtLog.objects.filter(thought_type="scene_match").first()
        self.assertIsNotNone(thought)
        self.assertIn("castle", thought.thought)
