import pytest

pytest.importorskip("django")

from assistants.models import SymbolicUXPlaybook, RoleDrivenUITemplate, Assistant
from agents.models import SwarmCodex


def test_phase11_9_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="oracle")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="ui")
    playbook = SymbolicUXPlaybook.objects.create(
        playbook_name="Oracle Mystic",
        archetype="oracle",
        tone_profile="mystic",
        ui_patterns={"panel": "overlay"},
    )
    playbook.codex_linked_rules.add(codex)

    template = RoleDrivenUITemplate.objects.create(
        template_name="Oracle Base",
        assigned_role="oracle",
        layout_config={"layout": "two-column"},
        aura_overlay="blue",
        active_traits=["wise"],
    )

    assert playbook.codex_linked_rules.count() == 1
    assert template.assigned_role == "oracle"
