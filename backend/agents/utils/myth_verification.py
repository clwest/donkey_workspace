from __future__ import annotations
from hashlib import sha256

from agents.models.lore import LoreToken, LoreTokenSignature, TemporalLoreAnchor, RitualComplianceRecord
from assistants.models.assistant import AssistantCivilization


def verify_lore_token_signature(token: LoreToken) -> bool:
    """Confirm hash of source memories matches signature."""
    try:
        signature = token.loretokensignature_set.latest("created_at")
    except LoreTokenSignature.DoesNotExist:
        return False

    data = "".join(m.content for m in token.source_memories.all())
    computed = sha256(data.encode()).hexdigest()
    if computed == signature.signature:
        signature.verified = True
        signature.save(update_fields=["verified"])
        return True
    return False


def sync_chronomyth_state():
    """Align lore anchors and ritual records across civilizations."""
    anchors = TemporalLoreAnchor.objects.all()
    civilizations = AssistantCivilization.objects.all()
    for civ in civilizations:
        for anchor in anchors:
            RitualComplianceRecord.objects.get_or_create(
                civilization=civ,
                anchor=anchor,
                defaults={"compliance_status": "pending"},
            )
