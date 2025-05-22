import json
from typing import Any, Dict, Optional
from utils.llm_router import call_llm
from assistants.models.assistant import Assistant
from assistants.models.thoughts import AssistantThoughtLog



def reflect_on_tool_output(
    tool_result: Any,
    tool_slug: str,
    original_input: Dict[str, Any],
    assistant: Assistant,
) -> Dict[str, Any]:
    """Use an LLM to evaluate a tool result and log a reflection."""
    prompt = (
        f"You are analysing the output of the tool '{tool_slug}'.\n"
        f"Input: {json.dumps(original_input)}\n"
        f"Output: {json.dumps(tool_result)}\n\n"
        "Respond in JSON with keys 'summary', 'useful' (true/false) and "
        "optional 'retry_input'."
    )

    try:
        text = call_llm(
            [{"role": "user", "content": prompt}],
            model="gpt-4o",
            temperature=0.3,
        )
    except Exception as e:  # pragma: no cover - network failure
        text = f"{{\"summary\": \"reflection failed: {e}\", \"useful\": true}}"

    try:
        data = json.loads(text[text.index("{") : text.rindex("}") + 1])
    except Exception:
        data = {"summary": text, "useful": True}

    summary = data.get("summary", "")
    useful = bool(data.get("useful", True))
    retry_input = data.get("retry_input")

    log = AssistantThoughtLog.objects.create(
        assistant=assistant,
        thought=summary,
        thought_type="reflection",
        event="tool_reflection",
        fallback_reason=None if useful else "tool_unsatisfactory",
        fallback_details={
            "tool": tool_slug,
            "original_input": original_input,
            "result": tool_result,
        },
    )

    return {
        "summary": summary,
        "useful": useful,
        "retry_input": retry_input,
        "log": log,
    }
