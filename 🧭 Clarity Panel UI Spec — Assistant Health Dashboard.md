🧭 Clarity Panel UI Spec — Assistant Health Dashboard

Purpose: Create a central UI route (/clarity) that provides a clear, assistant-by-assistant summary of system health, symbolic insight, and RAG effectiveness.

⸻

🔹 Route

Path: /clarity
Component: ClarityPanel.jsx
Backend: AssistantClaritySummaryView → /api/assistants/clarity/

⸻

🔍 View: Assistant Overview List

Column Description
Assistant Name + linked slug (badge: active/frozen)
Memories Total Memory Entries (🧠) + Reflections (🔁)
Glossary Anchors total, hits %, drift % (pie or ring)
Trust Score Composite score from fallbacks, mutation accuracy, insight yield
RAG Status Retrieval status: healthy / weak / broken (color + % fallback)
Prompt Latest prompt title + mutation count 🔧
Drift Sparkline or % showing recent symbolic mutation or change

⸻

🔍 View: Assistant Detail Drilldown (/clarity/:slug)

🧠 Memory Health
• Entry count
• Reflection coverage (per session)
• Top tags / memory types
• Orphaned / invalid status

📚 Glossary Overview
• Total symbolic anchors
• Hit ratio + fallback reasons
• Drift index + anchor retention
• Mutation log history

🧾 Prompt Diff
• Version history
• Last 3 mutations
• Linked reflection or Codex note

🔁 Replay/Drift Summary
• Session replays showing divergence or symbolic decay
• Anchors flagged as failing
• Suggest reflection rerun or prompt update

⸻

📊 Visual Elements
• Colored status tags (🟢 healthy, 🟡 weak, 🔴 broken)
• Trust score ring (out of 100)
• Anchor coverage chart (hits vs misses)
• Mutation feed (like git diff viewer for prompts)
• Export button (📥 Markdown / PDF)

⸻

🛠 Filters + Controls
• Assistant Search / Filter by tag or model
• Sort by fallback %, trust, glossary drift
• Button: Run Diagnostics (POST /api/assistants/:slug/refresh_clarity/)
• Export system state as JSON or MD

⸻

⚙️ Backend Response Schema (sample)

{
"assistant": "godelbot",
"status": "active",
"trust_score": 73,
"memory_count": 124,
"reflection_count": 26,
"glossary": {
"total": 72,
"hits": 19,
"drift": 0.23
},
"rag_fallback_rate": 0.38,
"prompt_title": "Recursive Architect",
"mutations": 4,
"symbolic_drift_score": 0.41
}

⸻

✅ MVP Goals
• /clarity route and base overview panel
• Assistant detail drilldown with symbolic and memory data
• Connect glossary mutation and trust metrics
• Integrate drift and prompt version viewer
• Add rerun diagnostics button per assistant
• Support export of assistant summary (md/pdf)

⸻

This panel helps users, devs, and assistants themselves understand how well they’re functioning and evolving. It is the mythic mirror for the symbolic swarm.
