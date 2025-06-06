import pytest
from django.core.management import call_command
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.models.assistant import (
    ChatSession,
    AssistantChatMessage,
    ChatIntentDriftLog,
)
from assistants.models.glossary import SuggestionLog
from memory.models import SymbolicMemoryAnchor
from assistants.utils.drift_detection import detect_drift_or_miss


@pytest.mark.django_db
def test_detect_drift_high_when_misses():
    assistant = Assistant.objects.create(name="A")
    SymbolicMemoryAnchor.objects.create(slug="evm", label="EVM")
    score, matches = detect_drift_or_miss("hello", assistant)
    assert score > 0.9
    assert matches == []


class DriftReviewCommandTest(BaseAPITestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.session = ChatSession.objects.create(assistant=self.assistant)
        msg = AssistantChatMessage.objects.create(
            session=self.session, role="user", content="hi"
        )
        for _ in range(3):
            ChatIntentDriftLog.objects.create(
                assistant=self.assistant,
                session=self.session,
                user_message=msg,
                drift_score=0.8,
                glossary_misses=["evm"],
            )

    def test_review_command_creates_suggestion(self):
        call_command(
            "review_first_message_drift", assistant=self.assistant.slug, threshold=0.5
        )
        assert (
            SuggestionLog.objects.filter(
                anchor_slug="evm", assistant=self.assistant
            ).count()
            == 1
        )
