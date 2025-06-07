from assistants.models.trail import TrailMarkerLog


def get_trail_editable_fields(marker: TrailMarkerLog, user) -> list[str]:
    """Return editable field names if the user owns the assistant."""
    if marker.assistant.created_by_id == getattr(user, "id", None):
        return ["user_note", "user_emotion", "is_starred"]
    return []

__all__ = ["get_trail_editable_fields"]
