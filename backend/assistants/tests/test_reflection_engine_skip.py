from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine

class ReflectionEngineSkipTest(BaseAPITestCase):
    def test_skip_when_no_memory_context(self):
        assistant = Assistant.objects.create(name="NoCtx", slug="noctx")
        engine = AssistantReflectionEngine(assistant)
        assert engine.reflect_now() is None
