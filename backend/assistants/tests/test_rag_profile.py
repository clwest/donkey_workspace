from unittest.mock import patch

from assistants.models import Assistant
from assistants.utils.rag_profile import generate_rag_profile_from_reflection
from memory.models import SymbolicMemoryAnchor


@patch("assistants.utils.rag_profile.get_embedding_for_text")
def test_generate_rag_profile(mock_embed, db):
    mock_embed.return_value = [0.1]
    anchor = SymbolicMemoryAnchor.objects.create(slug="evm", label="EVM")
    assistant = Assistant.objects.create(
        name="A",
        archetype="sage",
        dream_symbol="evm",
        init_reflection="evm focus",
    )

    result = generate_rag_profile_from_reflection(assistant)
    assistant.refresh_from_db()

    assert result["updated"] is True
    assert assistant.preferred_rag_vector == [0.1]
    assert assistant.anchor_weight_profile.get("evm") == 0.8
