
# Phase Ω.9.29 — Deep RAG Audit + Fallback Context Debugging

This phase is designed to investigate potential causes of grounding and retrieval failures in DonkGPT’s RAG system. It assumes all CLI tools and routes are functional but the assistant is still unable to inject relevant memory chunks into chats.

## ✅ Phase Summary

We observed persistent failures in RAG scoring, glossary injection, and reflection memory context. Multiple diagnostics show 0 chunk matches and 0 glossary impact, despite document linkage and prompt visibility. This phase coordinates a **deep dive** using both CLI commands and backend inspection.

---

## 🔎 Audit Steps

### 🧠 Embedding + Glossary Inspection

```shell
python manage.py glossary_anchor_health --assistant=donkgpt
python manage.py embed_missing_chunks
python manage.py inspect_glossary_fallbacks
```

### 🛠 Memory Link + Context Debugging

```shell
python manage.py inspect_memory_links --assistant=donkgpt
python manage.py repair_context_mismatches --assistant=donkgpt
```

### 🗂 Recovery + Reflection Hooks

```shell
python manage.py reflect_on_self --assistant=donkgpt
python manage.py sync_fallback_tags
```

---

## 🧪 Expected Observations

- Glossary anchors report 0 chunk matches for most terms (✅ confirmed)
- Memory entries mostly lack transcripts and show context mismatches
- Fallback tag sync logs no tagged memories
- Reflections fail to include glossary-based insight summaries

---

## 🧰 Suggested Codex Follow-ups

- Ensure `MemoryEntry.context` is consistently assigned and retrieved across chat, reflection, and recovery
- Add fallback_reason diagnostics to the RAG chunk retriever when **all chunks are filtered**
- Inject debug logs to verify glossary fingerprint comparison and chunk validity during scoring
- Link glossary fallback logs with session_id if available for better traceability

---

## 🧭 Outcome

This phase should surface the root cause of RAG grounding failures and empower Codex to patch missing fingerprint validation, fix memory linking, and ensure glossary boosts properly influence chunk score selection.

