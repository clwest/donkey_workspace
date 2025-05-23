import pytest

pytest.importorskip("django")

from assistants.models import Assistant, CodexLinkedGuild
from agents.models import (
    SwarmCodex,
    EncodedRitualBlueprint,
    GuildDeploymentKit,
    AssistantNetworkTransferProtocol,
    RitualFunctionContainer,
)


def test_phase16_5_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="seer")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="myth")
    guild = CodexLinkedGuild.objects.create(guild_name="G", codex=codex)
    ritual = EncodedRitualBlueprint.objects.create(name="R", encoded_steps=[])

    kit = GuildDeploymentKit.objects.create(
        guild=guild,
        symbolic_parameters={"p": 1},
        deployment_notes="n",
    )
    kit.included_codices.add(codex)
    kit.assistant_manifest.add(assistant)

    transfer = AssistantNetworkTransferProtocol.objects.create(
        assistant=assistant,
        source_network="net1",
        target_network="net2",
        symbolic_transfer_packet={"d": 1},
        codex_compatibility_log="ok",
    )

    container = RitualFunctionContainer.objects.create(
        ritual=ritual,
        assistant=assistant,
        execution_context={"e": 1},
        symbolic_input_log={"i": 2},
        result_trace="r",
        container_status="active",
    )

    assert kit.guild == guild
    assert transfer.assistant == assistant
    assert container.ritual == ritual
