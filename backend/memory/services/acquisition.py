from memory.models import SymbolicMemoryAnchor

__all__ = ["update_anchor_acquisition"]

ORDER = {
    "unseen": 0,
    "exposed": 1,
    "acquired": 2,
    "reinforced": 3,
}

def update_anchor_acquisition(anchor: SymbolicMemoryAnchor, stage: str) -> None:
    """Upgrade acquisition_stage if stage is higher."""
    if stage not in ORDER:
        return
    current = ORDER.get(anchor.acquisition_stage or "unseen")
    if ORDER[stage] > current:
        anchor.acquisition_stage = stage
        anchor.save(update_fields=["acquisition_stage"])
        if anchor.assistant_id:
            count = SymbolicMemoryAnchor.objects.filter(
                assistant_id=anchor.assistant_id,
                acquisition_stage__in=["acquired", "reinforced"],
            ).count()
            anchor.assistant.glossary_score = count
            anchor.assistant.save(update_fields=["glossary_score"])
