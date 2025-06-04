import os
import logging
import requests
from openai import OpenAI
from intel_core.models import GlossaryUsageLog, GlossaryMissReflectionLog, DocumentChunk
from intel_core.services.acronym_glossary_service import AcronymGlossaryService
from memory.models import (
    SymbolicMemoryAnchor,
    GlossaryRetryLog,
    AnchorConvergenceLog,
)

DEFAULT_MODEL = "gpt-4o-mini"
client = OpenAI()
logger = logging.getLogger(__name__)

# Strict system prompt used whenever RAG chunks are injected
RAG_SYSTEM_PROMPT = """
You are a retrieval-grounded assistant. You must answer using the MEMORY CHUNKS below.

These chunks may come from a video transcript, PDF, or webpage. If a chunk contains the answer, summarize or quote it. You are allowed to provide direct information from these chunks.

If you are answering based on document memory, only proceed if the provided context score is above 0.65. If the score is lower, respond with:
"I didn’t find a strong match in my knowledge. Would you like to upload a new guide or try rephrasing the question?"

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


def chat(
    messages: list[dict],
    assistant,
    *,
    focus_anchors_only: bool = False,
    retry_on_miss: bool = False,
    enable_retry_logging: bool = False,
    force_chunks: bool = False,
    **kwargs,
) -> tuple[str, list[str], dict]:
    """High-level chat call that can summon memories and RAG context."""
    from assistants.utils.memory_summoner import summon_relevant_memories
    from assistants.utils.chunk_retriever import get_relevant_chunks, format_chunks

    assistant = assistant.__class__.objects.select_related("system_prompt").get(id=assistant.id)
    msgs = list(messages)
    system_prompt = assistant.system_prompt.content if assistant.system_prompt else None
    if system_prompt:
        logger.debug(
            "\U0001f9e0 Using prompt %s (%s) for assistant %s",
            assistant.system_prompt.title,
            assistant.system_prompt.id,
            assistant.slug,
        )
        replaced = False
        for idx, m in enumerate(msgs):
            if m.get("role") == "system":
                msgs[idx] = {"role": "system", "content": system_prompt}
                replaced = True
                break
        if not replaced:
            msgs.insert(0, {"role": "system", "content": system_prompt})
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
    auto_expand = kwargs.pop("auto_expand", False)
    (
        chunks,
        reason,
        fallback,
        glossary_present,
        top_score,
        top_chunk_id,
        glossary_forced,
        focus_fallback,
        filtered_anchor_terms,
        debug_info,
    ) = get_relevant_chunks(
        str(assistant.id),
        query_text,
        auto_expand=auto_expand,
        force_chunks=force_chunks,
    )
    invalid_chunks = [c for c in chunks if c.get("embedding_status") != "embedded"]
    if invalid_chunks:
        for ch in invalid_chunks:
            logger.warning(
                "\u26a0\ufe0f RAG selected chunk %s with embedding_status=%s",
                ch.get("chunk_id"),
                ch.get("embedding_status"),
            )
        chunks = [c for c in chunks if c.get("embedding_status") == "embedded"]
        top_score = 0.0
        fallback = True
        reason = "non-embedded"
        ids = ", ".join(ch.get("chunk_id") for ch in invalid_chunks)
        rag_meta.setdefault("debug_logs", []).append(
            f"Invalid embedding status for chunks: {ids}"
        )
    query_terms = AcronymGlossaryService.extract(query_text)
    all_anchors = list(SymbolicMemoryAnchor.objects.values_list("slug", flat=True))
    anchor_matches = [s for s in all_anchors if s.lower() in query_text.lower()]
    anchor_objs = SymbolicMemoryAnchor.objects.filter(slug__in=anchor_matches).order_by(
        "slug"
    )
    guidance_map = {
        a.slug: [
            line.strip() for line in a.glossary_guidance.split("\n") if line.strip()
        ]
        for a in anchor_objs
        if a.glossary_guidance
    }
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
        "glossary_forced": glossary_forced,
        "prompt_appended_glossary": False,
        "guidance_appended": False,
        "focus_fallback": focus_fallback,
        "filtered_anchor_terms": filtered_anchor_terms,
        "glossary_definitions": [],
        "glossary_guidance": sum(guidance_map.values(), []),
        "force_chunks": force_chunks,
    }
    rag_meta.update(debug_info)
    if fallback:
        rag_meta["weak_chunks_used"] = True
        if rag_meta.get("fallback_chunk_ids"):
            first_id = rag_meta["fallback_chunk_ids"][0]
            first_score = rag_meta["fallback_chunk_scores"][0]
            rag_meta.setdefault("debug_logs", []).append(
                f"\u26a0\ufe0f Weak context fallback: used chunk {first_id} (score {first_score})"
            )
    rag_meta["fallback_reason"] = reason
    retried = False
    retry_type = "standard"
    retry_log = None
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
        if fallback or focus_anchors_only:
            gloss_first = [c for c in chunks if c.get("is_glossary")]
            non_gloss = [c for c in chunks if not c.get("is_glossary")]
            chunks = gloss_first + non_gloss
        else:
            gloss_first = [c for c in chunks if c.get("is_glossary")]
        rag_meta["glossary_debug"] = [
            {"id": c["chunk_id"], "slug": c.get("anchor_slug"), "score": c["score"]}
            for c in gloss_first
        ]
        rag_meta["glossary_first"] = all(
            c in chunks[: len(gloss_first)] for c in gloss_first
        )
        logger.debug("Glossary chunks included: %s", rag_meta["glossary_debug"])
        rag_meta["rag_used"] = True
        rag_meta["rag_fallback"] = fallback
        rag_meta["used_chunks"] = [
            {
                "chunk_id": c["chunk_id"],
                "score": c["score"],
                "source_doc": c["source_doc"],
                "anchor_slug": c.get("anchor_slug"),
                "anchor_confidence": c.get("anchor_confidence"),
            }
            for c in chunks
        ]
        rag_meta["chunk_scores"] = [(c["chunk_id"], c["score"]) for c in chunks]
        rag_meta["glossary_chunk_ids"] = [
            c["chunk_id"] for c in chunks if c.get("is_glossary")
        ]
        rag_meta["glossary_used"] = bool(rag_meta["glossary_chunk_ids"])
        rag_meta["anchor_hits"] = [
            slug
            for slug in anchor_matches
            if any(c.get("anchor_slug") == slug for c in chunks)
        ]
        rag_meta["anchor_misses"] = [
            slug for slug in anchor_matches if slug not in rag_meta["anchor_hits"]
        ]
        for i, c in enumerate(chunks, 1):
            logger.info("Chunk %s chosen %.4f: %s", i, c["score"], c["text"][:80])
            if c["score"] < 0.45:
                logger.warning(
                    "\u26a0\ufe0f Low RAG score %.2f for chunk %s: %s",
                    c["score"],
                    c["chunk_id"],
                    c["text"][:80],
                )

        gloss_lines = []
        for info in chunks:
            if info.get("is_glossary"):
                text = info["text"].strip()
                if " refers to " in text:
                    term, definition = text.split(" refers to ", 1)
                    gloss_lines.append(f"- {term.strip()}: {definition.strip()}")
                else:
                    gloss_lines.append(f"- {text}")
        system_content = RAG_SYSTEM_PROMPT
        if gloss_lines:
            rag_meta["prompt_appended_glossary"] = True
            rag_meta["glossary_definitions"] = gloss_lines
            terms = []
            for line in gloss_lines:
                if ":" in line:
                    terms.append(line.split(":", 1)[0].lstrip("- "))
                elif " refers to " in line:
                    terms.append(line.split(" refers to ", 1)[0].lstrip("- "))
            if terms:
                term_list = ", ".join(f"'{t}'" for t in terms[:2])
                system_content += (
                    "\nYou have access to glossary definitions for key terms such as "
                    f"{term_list}. Use them when responding."
                )
            system_content += "\n\nGlossary Reference:\n" + "\n".join(gloss_lines)
            if guidance_map:
                hints = []
                for slug, lines in guidance_map.items():
                    for g in lines:
                        hints.append(f"- {g}")
                if hints:
                    system_content += "\n\nAnchor Guidance:\n" + "\n".join(hints)
                system_content += (
                    "\nYou are equipped with glossary-backed memory. Use the following reference definitions to guide user questions related to:\n"
                    + "\n".join(f"- Anchor: {s}" for s in guidance_map.keys())
                )
            system_content += "\nUse the above glossary definitions to answer the user's question unless contradicted by newer documents."
            rag_meta["guidance_appended"] = bool(guidance_map)

        replaced = False
        for idx, m in enumerate(msgs):
            if m.get("role") == "system":
                msgs[idx] = {"role": "system", "content": system_content}
                replaced = True
                break
        if not replaced:
            msgs.insert(0, {"role": "system", "content": system_content})

        guidance_block = []
        if gloss_lines:
            guidance_block = [
                "# Glossary Reference:",
                "You may refer to the following glossary entry for context:",
                "",
                *gloss_lines,
                "",
                "Use this to inform your answer. Do not ignore this context.",
                "ANCHOR:",
            ]
        lines = guidance_block + ["MEMORY CHUNKS", "=================="]
        for i, info in enumerate(chunks, 1):
            prefix = "[G] " if info.get("is_glossary") else ""
            lines.append(f"[{i}] {prefix}{info['text']}")
        if guidance_map:
            lines.append("-- Guidance --")
            for g in sum(guidance_map.values(), []):
                lines.append(f"- {g}")
        lines.append("==================")
        chunk_block = "\n".join(lines)
        logger.debug("Injecting chunk block: %s", chunk_block)

        last_user_idx = max(i for i, m in enumerate(msgs) if m.get("role") == "user")
        msgs.insert(last_user_idx, {"role": "user", "content": chunk_block})
    else:
        rag_meta["rag_used"] = False
        rag_meta["rag_ignored_reason"] = reason or "no matching chunks found"
        rag_meta["anchor_hits"] = []
        rag_meta["anchor_misses"] = anchor_matches
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
            from assistants.utils.assistant_thought_engine import (
                AssistantThoughtEngine,
            )

            engine = AssistantThoughtEngine(assistant=assistant)
            try:
                missing_anchor = anchor_matches[0] if anchor_matches else ""
                gloss_reflection = engine.reflect_on_rag_failure(
                    query_text, missing_anchor
                )
                gloss_log.reflected_on = True
                gloss_log.save(update_fields=["reflected_on"])
                from assistants.models.glossary import AssistantGlossaryLog

                AssistantGlossaryLog.objects.create(
                    assistant=assistant,
                    query=query_text,
                    anchor=SymbolicMemoryAnchor.objects.filter(
                        slug=missing_anchor
                    ).first(),
                    ignored=True,
                )
            except Exception:
                logger.exception("Failed to reflect on glossary miss")
                gloss_reflection = None

    logger.debug("Final messages array: %s", msgs)
    reply = call_llm(
        msgs, model=getattr(assistant, "preferred_model", DEFAULT_MODEL), **kwargs
    )
    first_reply = reply
    if rag_meta.get("glossary_debug"):
        ignored = []
        for g in rag_meta["glossary_debug"]:
            term = (g.get("slug") or "").lower()
            if term and term not in reply.lower():
                ignored.append(g["id"])
        rag_meta["glossary_ignored"] = ignored
        logger.debug("Glossary chunks ignored by LLM: %s", ignored)
    escalate = (
        rag_meta.get("glossary_present")
        and rag_meta.get("guidance_appended")
        and rag_meta.get("glossary_ignored")
    )
    if escalate:
        msgs.insert(
            0,
            {
                "role": "system",
                "content": "The following glossary definition is authoritative. Use it unless explicitly contradicted by more recent sources.",
            },
        )
        reply = call_llm(
            msgs, model=getattr(assistant, "preferred_model", DEFAULT_MODEL), **kwargs
        )
        retried = True
        retry_type = "escalated"
        rag_meta["escalated_retry"] = True
    else:
        rag_meta["escalated_retry"] = False
    if rag_meta.get("anchor_misses"):
        rag_meta["anchor_misses"] = [
            s for s in rag_meta["anchor_misses"] if s.lower() not in reply.lower()
        ]
    refusal_phrases = [
        "can't access",
        "not in memory",
        "don't have access",
    ]
    if any(p in reply.lower() for p in refusal_phrases):
        logger.warning(
            "⚠️ Assistant hallucinated access refusal. RAG was likely not respected."
        )
        if glossary_forced:
            try:
                from assistants.models.glossary import AssistantGlossaryLog

                AssistantGlossaryLog.objects.create(
                    assistant=assistant,
                    query=query_text,
                    anchor=(
                        SymbolicMemoryAnchor.objects.filter(
                            slug=anchor_matches[0]
                        ).first()
                        if anchor_matches
                        else None
                    ),
                    ignored=True,
                )
            except Exception:
                logger.exception("Failed to log glossary refusal")

    if (
        rag_meta.get("glossary_present")
        and rag_meta.get("rag_used")
        and ("couldn't" in reply.lower() or "could not" in reply.lower())
    ):
        try:
            anchor_slug = rag_meta.get("anchor_hits", [])
            if not anchor_slug:
                anchor_slug = rag_meta.get("anchors", [])
                anchor = (
                    SymbolicMemoryAnchor.objects.filter(slug=anchor_slug[0]).first()
                    if anchor_slug
                    else None
                )
                if anchor:
                    from assistants.utils.assistant_thought_engine import (
                        AssistantThoughtEngine,
                    )

                    engine = AssistantThoughtEngine(assistant=assistant)
                definition = rag_meta.get("glossary_definitions", [""])[0]
                reflection_text = engine.reflect_on_glossary_gap(
                    query_text, anchor.slug, definition
                )
                miss_log = GlossaryMissReflectionLog.objects.create(
                    anchor=anchor,
                    user_question=query_text,
                    assistant_response=reply,
                    glossary_chunk_ids=rag_meta.get("glossary_chunk_ids", []),
                    score_snapshot=dict(rag_meta.get("chunk_scores", [])),
                    reflection=reflection_text,
                )
                used_ids = [c["chunk_id"] for c in rag_meta.get("used_chunks", [])]
                matched = DocumentChunk.objects.filter(id__in=used_ids)
                if matched:
                    miss_log.matched_chunks.add(*matched)

                from intel_core.models import GlossaryFallbackReflectionLog

                GlossaryFallbackReflectionLog.objects.create(
                    anchor_slug=anchor.slug,
                    chunk_id=(
                        rag_meta.get("glossary_chunk_ids", [""])[0]
                        if rag_meta.get("glossary_chunk_ids")
                        else ""
                    ),
                    match_score=rag_meta.get("retrieval_score", 0.0),
                    assistant_response=reply,
                    glossary_injected=rag_meta.get("prompt_appended_glossary", False),
                )
                if retry_on_miss:
                    retried = True
                    msgs.append(
                        {
                            "role": "user",
                            "content": "Given the glossary context, revise your response.",
                        }
                    )
                    reply = call_llm(
                        msgs,
                        model=getattr(assistant, "preferred_model", DEFAULT_MODEL),
                        **kwargs,
                    )
            else:
                logger.warning(
                    "Glossary miss reflection skipped: no anchor found for %s",
                    anchor_slug,
                )
        except Exception:
            logger.exception("Failed to log glossary miss reflection")

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
            spawn_trigger="glossary_miss",
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
            spawn_trigger=(
                "rag_fallback" if rag_meta.get("rag_fallback") else "rag_unused"
            ),
        )
    elif rag_meta.get("anchor_misses"):
        from assistants.utils.assistant_thought_engine import AssistantThoughtEngine

        engine = AssistantThoughtEngine(assistant=assistant)
        miss_slug = rag_meta["anchor_misses"][0]
        try:
            anchor_reflection = engine.reflect_on_anchor_miss(query_text, miss_slug)
            from prompts.utils.mutation import (
                mutate_prompt_from_reflection,
                fork_assistant_from_prompt,
            )

            mutated = mutate_prompt_from_reflection(
                assistant,
                reflection_log=anchor_reflection,
                reason=f"anchor_miss:{miss_slug}",
            )
            label = (
                SymbolicMemoryAnchor.objects.filter(slug=miss_slug).first().label
                if miss_slug
                else miss_slug
            )
            fork_assistant_from_prompt(
                assistant,
                mutated.content
                + f"\nAlways explain '{label}' when referenced or relevant.",
                reflection=anchor_reflection,
                reason=f"anchor_miss:{miss_slug}",
                spawn_trigger=f"anchor_miss:{miss_slug}",
            )
        except Exception:
            logger.exception("Failed to reflect on anchor miss")

    if enable_retry_logging and (retried or rag_meta.get("glossary_ignored")):
        anchor_obj = (
            SymbolicMemoryAnchor.objects.filter(slug=anchor_matches[0]).first()
            if anchor_matches
            else None
        )
        before = (
            1.0
            if anchor_matches and anchor_matches[0].lower() in first_reply.lower()
            else 0.0
        )
        after = (
            1.0
            if anchor_matches and anchor_matches[0].lower() in reply.lower()
            else 0.0
        )
        retry_log = GlossaryRetryLog.objects.create(
            anchor=anchor_obj,
            anchor_slug=anchor_obj.slug if anchor_obj else "",
            question=query_text,
            first_response=first_reply,
            retry_response=reply if retried else None,
            glossary_chunk_ids=rag_meta.get("glossary_chunk_ids", []),
            guidance_injected=rag_meta.get("prompt_appended_glossary", False),
            retried=retried,
            retry_type=retry_type,
            score_diff=after - before,
        )

        rag_meta["glossary_retry_id"] = str(retry_log.id)
        rag_meta["score_diff"] = retry_log.score_diff
        rag_meta["retry_type"] = retry_type

    if rag_meta.get("glossary_used") and reply and not rag_meta.get("anchor_misses"):
        anchor_slug = (
            rag_meta.get("anchor_hits") or rag_meta.get("anchors") or [None]
        )[0]
        anchor_obj = (
            SymbolicMemoryAnchor.objects.filter(slug=anchor_slug).first()
            if anchor_slug
            else None
        )
        if anchor_obj:
            conv_log = AnchorConvergenceLog.objects.create(
                anchor=anchor_obj,
                assistant=assistant,
                guidance_used=rag_meta.get("guidance_appended", False),
                retried=retried,
                final_score=rag_meta.get("retrieval_score", 0.0),
            )
            rag_meta["convergence_log_id"] = str(conv_log.id)
            if not anchor_obj.reinforced_by.filter(id=assistant.id).exists():
                anchor_obj.reinforced_by.add(assistant)

    return reply, summoned, rag_meta
