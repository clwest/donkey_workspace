from typing import Dict


def explain_reasoning(trace: Dict) -> str:
    """Return a short explanation of how reasoning trace shaped the reply."""
    memories = trace.get("used_memories") or []
    anchors = trace.get("anchors") or []
    reflections = trace.get("reflections") or []
    mem_part = (
        f"memories related to {', '.join(memories[:2])}"
        if memories
        else "recent context"
    )
    anchor_part = f"terms like '{anchors[0]}'" if anchors else "general knowledge"
    refl_part = (
        f"a reflection on {reflections[0]}" if reflections else "general insight"
    )
    return (
        f"I used {mem_part} and relied on glossary {anchor_part}. "
        f"Additionally, {refl_part} informed this response."
    )
