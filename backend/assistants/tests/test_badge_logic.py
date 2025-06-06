from django.test import TestCase
from assistants.models import Assistant, Badge
from memory.models import SymbolicMemoryAnchor
from assistants.models.reflection import AssistantReflectionLog
from assistants.utils.badge_logic import update_assistant_badges


class BadgeLogicTest(TestCase):
    def test_update_assistant_badges(self):
        a = Assistant.objects.create(name="Badge", specialty="test")
        Badge.objects.create(
            slug="glossary_apprentice", label="GA", criteria="acquired>=10"
        )
        Badge.objects.create(
            slug="semantic_master", label="SM", criteria="reinforced>=25"
        )
        Badge.objects.create(
            slug="reflection_ready", label="RR", criteria="reflections>=5"
        )
        Badge.objects.create(
            slug="vocab_proficient", label="VP", criteria="glossary_score>=50"
        )
        Badge.objects.create(
            slug="replay_scholar", label="RS", criteria="improved_replays>=3"
        )
        Badge.objects.create(
            slug="delegation_ready", label="DR", criteria="badge_count>=3"
        )

        for i in range(25):
            anchor = SymbolicMemoryAnchor.objects.create(slug=f"t{i}", label=f"T{i}")
            anchor.reinforced_by.add(a)
            if i < 10:
                anchor.assistant = a
                anchor.save()
        for i in range(5):
            AssistantReflectionLog.objects.create(
                assistant=a, title=f"r{i}", summary="s"
            )

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

    def test_manual_override(self):
        a = Assistant.objects.create(name="Badge2", specialty="t")
        Badge.objects.create(
            slug="reflection_ready", label="RR", criteria="reflections>=5"
        )

        update_assistant_badges(a)
        a.refresh_from_db()
        assert "reflection_ready" not in a.skill_badges

        update_assistant_badges(a, manual={"reflection_ready": True}, override=True)
        a.refresh_from_db()
        assert "reflection_ready" in a.skill_badges
        assert len(a.badge_history) == 1

        update_assistant_badges(a, manual={"reflection_ready": False}, override=True)
        a.refresh_from_db()
        assert "reflection_ready" not in a.skill_badges
