from .models import MythflowSession, SymbolicDialogueExchange


def calculate_narrative_pressure(session_id: int) -> dict:
    """Basic entropy and tension calculation for a mythflow session."""
    try:
        session = MythflowSession.objects.get(id=session_id)
    except MythflowSession.DoesNotExist:
        return {"detail": "session not found"}

    entropy = session.memory_trace.count()
    unresolved_tension = max(session.participants.count() - 1, 0)
    stagnation = SymbolicDialogueExchange.objects.filter(session=session).count()

    pressure = entropy + unresolved_tension - stagnation
    return {
        "entropy": entropy,
        "unresolved_role_tension": unresolved_tension,
        "stagnation_index": stagnation,
        "narrative_pressure": pressure,
    }
