import json
from memory.models import MemoryEntry
from .reflection_helpers import resolve_tags_from_names
from insights.models import AssistantInsightLog
from prompts.utils.openai_utils import complete_chat


def run_chat_reflection(assistant, user, limit=5):
    messages = (
        MemoryEntry.objects.filter(assistant=assistant, is_conversation=True)
        .order_by("-created_at")[:limit]
    )
    if not messages:
        return None

    transcript = "\n".join(
        f"{m.source_role}: {m.summary or m.event}" for m in reversed(messages)
    )
    prompt = (
        "Summarize the user's requests and propose improvements to the assistant's"
        " system prompt if it seems confused. Respond in JSON with keys: summary,"
        " tags, proposed_prompt."
    )
    output = complete_chat(
        system="You analyze chat history for improvement opportunities.",
        user=f"{transcript}\n\n{prompt}",
        max_tokens=300,
        temperature=0.3,
    )
    data = {"summary": output.strip(), "tags": [], "proposed_prompt": None}
    if "{" in output:
        try:
            json_part = output[output.index("{") : output.rindex("}") + 1]
            data = json.loads(json_part)
        except Exception:
            pass
    log = AssistantInsightLog.objects.create(
        assistant=assistant,
        user=user,
        summary=data.get("summary", output),
        tags=data.get("tags", []),
        proposed_prompt=data.get("proposed_prompt"),
    )
    return log
