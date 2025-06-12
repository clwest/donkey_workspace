🧠 Assistant Lifecycle

This document defines the full assistant journey from onboarding to adaptive growth. It is the canonical guide for ensuring user-facing assistants feel alive, responsive, and personalized.

⸻

1. 🎉 Creation (First Launch)
   • User signs up and is guided to create their first assistant.
   • Assistant is created with:
   • created_by: user
   • is_primary: true
   • memory_context is created and linked
   • primary_assistant_slug is stored in the UserProfile
   • Onboarding is marked complete for the user

✅ Sets the foundation for all future memory, document linking, and context-awareness.

⸻

2. 🧩 Setup (World-Building)
   • The assistant walks the user through their MythPath setup:
   • World → Domain / Expertise
   • Glossary → Key terms for user’s world
   • Archetype → Personality / Communication style
   • Summon → Final assistant creation
   • A default system prompt is generated using this setup
   • Assistant is optionally linked to starter documents or demo prompts

✅ This defines how the assistant speaks, thinks, and what it values.

⸻

3. 📚 Ingestion & Memory Context
   • User uploads documents (PDFs, YouTube links, URLs)
   • Each document is assigned:
   • assistant: linked to the user’s assistant
   • memory_context: same as assistant
   • session_id: used for chunk grouping and embedding traceability
   • Document is chunked, embedded, and linked to the assistant
   • Reflections run post-ingest to generate:
   • Summary
   • Glossary suggestions
   • Symbolic anchors

✅ Makes the assistant aware of documents the user wants it to study.

⸻

4. 💬 Interaction (Chat + Thought Capture)
   • User chats with the assistant
   • Every message is saved to MemoryEntry
   • Reflection logs track long-term observations
   • Assistants tag messages and propose glossary additions
   • Chain-of-thought is visible on the frontend

✅ Enables assistant to reflect on how it is being used and evolve from chat logs.

⸻

5. 🔁 Growth Loop (Self-Evolution)
   • Reflections scan all memory entries and recent document chunks
   • Drift is measured: is the assistant deviating from its intended behavior?
   • The assistant proposes self-updates:
   • Prompt refinements
   • Glossary expansions
   • Delegation to specialized sub-assistants
   • Optionally triggers:
   • Document Recovery: reprocess failed chunks
   • RAG Debug: inspect recall failures
   • System Prompt Regeneration

✅ Allows assistants to improve automatically based on usage and user content.

⸻

6. 🌱 User Feedback Loop
   • Users can:
   • 👍/👎 rate messages
   • Suggest edits to assistant memory or reflections
   • Add missing glossary terms
   • This feedback is stored and used in training, trust metrics, and assistant shaping

✅ Makes the system feel responsive and user-aligned.

⸻

7. 🛠️ System Health and Debugging
   • Every assistant exposes:
   • RAG Diagnostics
   • Memory Graph
   • Symbolic Glossary health
   • The /assistants/:slug/debug view shows:
   • Embedded chunk score distributions
   • Glossary misses
   • Linkage errors

✅ Surfaces issues like chunk drift, embedding loss, or anchor failures.

⸻

✅ Assistant Is Now Fully Alive

Once all layers are active:
• Chat uses documents
• Reflections evolve prompts
• User input shapes memory
• The assistant learns, adapts, and reflects

⸻

If an assistant cannot retrieve knowledge, propose updates, or adapt to feedback — it is not alive.

⸻

This lifecycle enables every assistant to become a personalized researcher, planner, and collaborator. Integrate each stage gradually, then optimize the loop for depth and longevity.
