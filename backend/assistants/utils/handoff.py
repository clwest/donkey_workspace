from assistants.models import ChatSession, AssistantChatMessage
from prompts.utils.openai_utils import complete_chat


def generate_handoff_summary(session: ChatSession, limit: int = 15) -> str:
    """Return a short summary of recent conversation for session handoff."""
    messages = (
        AssistantChatMessage.objects.filter(session=session)
        .order_by("-created_at")[:limit]
    )
    lines = []
    for m in reversed(list(messages)):
        lines.append(f"{m.role.title()}: {m.content}")
    prompt = "\n".join(lines)
    system = (
        "You summarize chat history for another assistant who will take over."
        " Provide key points and current goals in 3-5 sentences."
    )
    try:
        summary = complete_chat(system=system, user=prompt, max_tokens=150, temperature=0.3)
        return summary
    except Exception:
        return "\n".join(lines)[:500]
