from django.test import TestCase
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor
from assistants.models.reflection import AssistantReflectionLog
from assistants.utils.badge_logic import update_assistant_badges


class BadgeLogicTest(TestCase):
    def test_update_assistant_badges(self):
        a = Assistant.objects.create(name="Badge", specialty="test")
        for i in range(25):
            anchor = SymbolicMemoryAnchor.objects.create(slug=f"t{i}", label=f"T{i}")
            anchor.reinforced_by.add(a)
            if i < 10:
                anchor.assistant = a
                anchor.save()
        for i in range(5):
            AssistantReflectionLog.objects.create(assistant=a, title=f"r{i}", summary="s")

        update_assistant_badges(a)
        a.refresh_from_db()
        assert "glossary_apprentice" in a.skill_badges
        assert "semantic_master" in a.skill_badges
        assert "reflection_ready" in a.skill_badges
        assert "delegation_ready" in a.skill_badges
        assert "vocab_proficient" not in a.skill_badges

        a.glossary_score = 60
        a.save(update_fields=["glossary_score"])
        update_assistant_badges(a)
        a.refresh_from_db()
        assert "vocab_proficient" in a.skill_badges
