import os
import logging
import requests
from openai import OpenAI
from intel_core.models import GlossaryUsageLog
from intel_core.services.acronym_glossary_service import AcronymGlossaryService
from memory.models import SymbolicMemoryAnchor
from assistants.utils.assistant_thought_engine import AssistantThoughtEngine

DEFAULT_MODEL = "gpt-4o-mini"
client = OpenAI()
logger = logging.getLogger(__name__)

# Strict system prompt used whenever RAG chunks are injected
RAG_SYSTEM_PROMPT = """
You are a retrieval-grounded assistant. You must answer using the MEMORY CHUNKS below.

These chunks may come from a video transcript, PDF, or webpage. If a chunk contains the answer, summarize or quote it. You are allowed to provide direct information from these chunks.

If you don’t find an answer in memory, say: “I couldn’t find that information in the provided memory.”
"""


def _call_openai(messages: list[dict], model: str, **kwargs) -> str:
    logger.info("Calling OpenAI with model %s", model)
    logger.debug("OpenAI payload: %s", {"model": model, "messages": messages})
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


def chat(messages: list[dict], assistant, **kwargs) -> tuple[str, list[str], dict]:
    """High-level chat call that can summon memories and RAG context."""
    from assistants.utils.memory_summoner import summon_relevant_memories
    from assistants.utils.chunk_retriever import get_relevant_chunks, format_chunks

    msgs = list(messages)
    summoned: list[str] = []
    if getattr(assistant, "memory_summon_enabled", False):
        user_parts = [m.get("content", "") for m in msgs if m.get("role") == "user"]
        prompt_text = "\n".join(user_parts[-1:])
        injection, summoned = summon_relevant_memories(prompt_text, assistant)
        if injection:
            msgs.append({"role": "system", "content": injection})

    # RAG chunk retrieval
    user_parts = [m.get("content", "") for m in msgs if m.get("role") == "user"]
    query_text = user_parts[-1] if user_parts else ""
    chunks, reason, fallback, glossary_present, top_score, top_chunk_id = (
        get_relevant_chunks(str(assistant.id), query_text)
    )
    query_terms = AcronymGlossaryService.extract(query_text)
    all_anchors = list(SymbolicMemoryAnchor.objects.values_list("slug", flat=True))
    anchor_matches = [s for s in all_anchors if s.lower() in query_text.lower()]
    rag_meta = {
        "rag_used": False,
        "used_chunks": [],
        "rag_ignored_reason": None,
        "rag_fallback": False,
        "glossary_present": glossary_present,
        "retrieval_score": top_score,
        "glossary_used": False,
        "glossary_terms": list(query_terms.keys()),
        "glossary_chunk_ids": [],
        "glossary_fallback": False,
        "anchors": anchor_matches,
        "chunk_scores": [],
    }
    gloss_log = GlossaryUsageLog.objects.create(
        query=query_text,
        rag_used=bool(chunks),
        glossary_present=glossary_present,
        retrieval_score=top_score,
        assistant=assistant,
        linked_chunk_id=top_chunk_id,
    )
    gloss_reflection = None
    if chunks:
        rag_meta["rag_used"] = True
        rag_meta["rag_fallback"] = fallback
        rag_meta["used_chunks"] = [
            {
                "chunk_id": c["chunk_id"],
                "score": c["score"],
                "source_doc": c["source_doc"],
                "anchor_slug": c.get("anchor_slug"),
            }
            for c in chunks
        ]
        rag_meta["chunk_scores"] = [(c["chunk_id"], c["score"]) for c in chunks]
        rag_meta["glossary_chunk_ids"] = [
            c["chunk_id"] for c in chunks if c.get("is_glossary")
        ]
        rag_meta["glossary_used"] = bool(rag_meta["glossary_chunk_ids"])
        for i, c in enumerate(chunks, 1):
            logger.info("Chunk %s chosen %.4f: %s", i, c["score"], c["text"][:80])
            if c["score"] < 0.45:
                logger.warning(
                    "\u26a0\ufe0f Low RAG score %.2f for chunk %s: %s",
                    c["score"],
                    c["chunk_id"],
                    c["text"][:80],
                )

        replaced = False
        for idx, m in enumerate(msgs):
            if m.get("role") == "system":
                msgs[idx] = {"role": "system", "content": RAG_SYSTEM_PROMPT}
                replaced = True
                break
        if not replaced:
            msgs.insert(0, {"role": "system", "content": RAG_SYSTEM_PROMPT})

        lines = ["MEMORY CHUNKS", "=================="]
        for i, info in enumerate(chunks, 1):
            lines.append(f"[{i}] {info['text']}")
        lines.append("==================")
        chunk_block = "\n".join(lines)
        logger.debug("Injecting chunk block: %s", chunk_block)

        last_user_idx = max(i for i, m in enumerate(msgs) if m.get("role") == "user")
        msgs.insert(last_user_idx, {"role": "user", "content": chunk_block})
    else:
        rag_meta["rag_used"] = False
        rag_meta["rag_ignored_reason"] = reason or "no matching chunks found"
        if anchor_matches and query_terms:
            rag_meta["glossary_fallback"] = True
            rag_meta["glossary_reason"] = "No glossary chunk matched known anchors"

        logger.warning(
            "\u26a0\ufe0f No relevant chunks found — skipping memory injection"
        )
        if glossary_present:
            logger.info("Glossary present but unused")
            from memory.services import MemoryService
            from mcp_core.models import Tag

            tag, _ = Tag.objects.get_or_create(
                slug="missed_glossary_context",
                defaults={"name": "missed_glossary_context"},
            )
            mem = MemoryService.create_entry(
                event=f"Glossary unused for query: {query_text}\nChunk: {top_chunk_id}",
                assistant=assistant,
                source_role="system",
            )
            mem.tags.add(tag)
            engine = AssistantThoughtEngine(assistant=assistant)
            try:
                missing_anchor = anchor_matches[0] if anchor_matches else ""
                gloss_reflection = engine.reflect_on_rag_failure(
                    query_text, missing_anchor
                )
                gloss_log.reflected_on = True
                gloss_log.save(update_fields=["reflected_on"])
            except Exception:
                logger.exception("Failed to reflect on glossary miss")
                gloss_reflection = None

    logger.debug("Final messages array: %s", msgs)
    reply = call_llm(
        msgs, model=getattr(assistant, "preferred_model", DEFAULT_MODEL), **kwargs
    )
    if "I can’t access" in reply or "I can't provide" in reply:
        logger.warning(
            "⚠️ Assistant hallucinated access refusal. RAG was likely not respected."
        )

    if gloss_reflection:
        from prompts.utils.mutation import (
            mutate_prompt_from_reflection,
            fork_assistant_from_prompt,
        )

        mutated = mutate_prompt_from_reflection(
            assistant,
            reflection_log=gloss_reflection,
            reason="Glossary recall failure",
        )
        fork_assistant_from_prompt(
            assistant,
            mutated.content
            + "\nIf glossary definitions are included in memory, use them verbatim.",
            reflection=gloss_reflection,
            reason="Glossary recall failure",
        )
    elif (not rag_meta.get("rag_used") or rag_meta.get("rag_fallback")) and (
        "couldn't" in reply.lower() or "could not" in reply.lower()
    ):
        from assistants.models.reflection import AssistantReflectionLog
        from prompts.utils.mutation import (
            mutate_prompt_from_reflection,
            fork_assistant_from_prompt,
        )

        reflection = AssistantReflectionLog.objects.create(
            assistant=assistant,
            title="Prompt Restriction",
            summary="Assistant was unable to answer due to prompt restriction.",
        )
        mutated_prompt = mutate_prompt_from_reflection(
            assistant,
            reflection_log=reflection,
            reason="rag_fallback" if rag_meta.get("rag_fallback") else "rag_unused",
        )
        fork_assistant_from_prompt(
            assistant,
            mutated_prompt.content,
            reflection=reflection,
        )

    return reply, summoned, rag_meta
