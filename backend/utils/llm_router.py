import os
import requests
from openai import OpenAI

DEFAULT_MODEL = "gpt-4o"
client = OpenAI()


def _call_openai(messages: list[dict], model: str, **kwargs) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        **kwargs,
    )
    return response.choices[0].message.content.strip()


def _call_ollama(messages: list[dict], model: str, **kwargs) -> str:
    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    url = f"{base.rstrip('/')}/api/chat"
    payload = {"model": model, "messages": messages}
    payload.update(kwargs)
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    data = resp.json()
    if "message" in data and isinstance(data["message"], dict):
        return data["message"].get("content", "").strip()
    if data.get("choices"):
        return data["choices"][0]["message"]["content"].strip()
    return ""


def _call_openrouter(messages: list[dict], model: str, **kwargs) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")
    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = {"model": model, "messages": messages}
    payload.update(kwargs)
    headers = {"Authorization": f"Bearer {api_key}"}
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def call_llm(messages: list[dict], model: str = DEFAULT_MODEL, **kwargs) -> str:
    """Route LLM calls to OpenAI, Ollama, or OpenRouter based on model name."""
    if not messages:
        raise ValueError("messages list is required")
    if ":" in model:
        prefix, actual = model.split(":", 1)
        if prefix == "ollama":
            return _call_ollama(messages, actual, **kwargs)
        if prefix == "openrouter":
            return _call_openrouter(messages, actual, **kwargs)
        if prefix == "openai":
            return _call_openai(messages, actual, **kwargs)
        raise ValueError(f"Unsupported model: {model}")
    else:
        return _call_openai(messages, model, **kwargs)


def chat(messages: list[dict], assistant, **kwargs) -> tuple[str, list[str]]:
    """High-level chat call that can summon memories."""
    from assistants.utils.memory_summoner import summon_relevant_memories

    msgs = list(messages)
    summoned: list[str] = []
    if getattr(assistant, "memory_summon_enabled", False):
        user_parts = [m.get("content", "") for m in msgs if m.get("role") == "user"]
        prompt_text = "\n".join(user_parts[-1:])
        injection, summoned = summon_relevant_memories(prompt_text, assistant)
        if injection:
            msgs.append({"role": "system", "content": injection})

    reply = call_llm(
        msgs, model=getattr(assistant, "preferred_model", DEFAULT_MODEL), **kwargs
    )
    return reply, summoned
