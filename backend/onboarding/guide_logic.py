from assistants.models import Assistant, AssistantHintState
from assistants.models.reflection import AssistantReflectionLog
from memory.models import SymbolicMemoryAnchor, RAGGroundingLog


def get_hint_status(user):
    """Return a mapping of hint_id -> status (seen/dismissed)."""
    assistant = (
        Assistant.objects.filter(created_by=user).order_by("created_at").first()
    )
    if not assistant:
        return {}
    states = AssistantHintState.objects.filter(user=user, assistant=assistant)
    status = {}
    for s in states:
        status[s.hint_id] = "dismissed" if s.dismissed else "seen"
    return status


def suggest_next_hint(user):
    """Return (hint_id, ui_action) for the next hint if applicable."""
    assistant = (
        Assistant.objects.filter(created_by=user).order_by("created_at").first()
    )
    if not assistant:
        return None, None

    state_map = {
        s.hint_id: s for s in AssistantHintState.objects.filter(
            user=user, assistant=assistant
        )
    }

    # Glossary tour if no anchors taught
    if (
        "glossary_tour" not in state_map
        and not SymbolicMemoryAnchor.objects.filter(
            assistant=assistant,
            acquisition_stage__in=["acquired", "reinforced"],
        ).exists()
    ):
        return "glossary_tour", f"goto:/assistants/{assistant.slug}/glossary"

    # RAG intro if no reflections or rag logs
    if (
        "rag_intro" not in state_map
        and not AssistantReflectionLog.objects.filter(assistant=assistant).exists()
        and not RAGGroundingLog.objects.filter(assistant=assistant).exists()
    ):
        return "rag_intro", f"goto:/assistants/{assistant.slug}/rag_debug"

    return None, None
