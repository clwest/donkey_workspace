🧠 RAG Debug Overview

This document summarizes the key differences and use cases for the two main RAG debugging routes used in the Donkey Workspace system. These tools are essential for tracking assistant retrieval accuracy, grounding failures, and glossary anchor health.

⸻

🔍 1. RAG Grounding Inspector

Route: /assistants/:slug/rag-inspector
Component: RagGroundingInspectorPage

📌 Description:

Displays a global log of assistant RAG queries from the RAGGroundingLog table. Each entry reflects a single grounding attempt and includes:
• Query string
• Number of chunks searched
• Final score (with raw + boosted info under the hood)
• Fallback warning icon
• Glossary hits and misses
• Quick Boost links

✅ Use Cases:
• Identify frequent low-score or fallback queries
• Spot glossary terms that consistently miss
• Queue mutation suggestions
• Drill into term-level RAG behavior across all memory chunks

🔧 Example Tools:
• Boost buttons
• Review Mutation Suggestions

⸻

🧩 2. RAG Debug Panel (Anchor-Specific View)

Route: /assistants/:slug/rag-debug
Component: RAGDebugPanel or anchor-scoped debug inspector

📌 Description:

Used for diagnosing issues with a single glossary anchor. This panel provides:
• Retrieval scores over time
• Matched / missed chunks
• Reflections associated with the anchor
• Last chunk match

✅ Use Cases:
• Deep-dive into glossary drift
• Evaluate how an anchor is reinforced or failing
• Anchor-by-anchor investigation for debugging or tuning

🔧 Tools Included:
• Score tracker by anchor
• Chunk-level score display
• Anchor-linked reflections panel

⸻

🤝 When to Use Which

Task Use rag-inspector Use rag-debug
Find bad glossary terms ✅ Yes ❌ No
Diagnose a single anchor ❌ No ✅ Yes
Accept/Reject mutations ✅ Yes (via inspector) ❌ Not supported
View fallback reasons ✅ Yes ✅ Yes
Review chunk scoring ✅ Global view ✅ Focused view

⸻

🚀 Future Integration Ideas
• Link rag-inspector terms directly into rag-debug for smooth navigation
• Display anchor health badges from rag-debug in the inspector
• Include anchor protection and reinforcement logs in both views

⸻

Last updated: 2025-06-06
