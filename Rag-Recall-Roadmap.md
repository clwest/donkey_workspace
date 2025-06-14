📘 RAG Recovery and Optimization Roadmap (Phase Ω.10.t–Ω.10.w)

This document outlines the next logical stages of RAG (Retrieval-Augmented Generation) recovery, scoring, and trust optimization work following the completion of Phase Ω.10.s (chunk linkage repair).

⸻

✅ Current RAG System Status (Post Ω.10.s)
• run_rag_tests and rag_tests.json working with question support
• run_rag_diagnostics completes and scores glossary anchors
• sync_missing_diagnostics handles anchor inference and scoring fallback
• validate_anchors, score_symbolic_anchors, track_anchor_drift operational
• relink_anchor_chunks links SymbolicMemoryAnchors to ChunkTag matches
• generate_diagnostic_reports succeeds but many anchors show low or 0 match
• UI reflects recall, drift, trust, and chunk linkage stats

⸻

🧠 Phase Plan: Ω.10.t → Ω.10.w

🔸 Ω.10.t — RAG Recall Booster

Goal: Suggest or mutate anchors with weak matches by analyzing nearby high-scoring chunks

Tasks:
• CLI: suggest_better_anchors
• Scan RAGGroundingLog for weak matches
• Identify high-score chunks within token radius
• Extract candidate tokens from chunk
• Compare with glossary anchors
• Suggest replacements, optionally auto-approve

⸻

🔸 Ω.10.u — Glossary Mutation & Cleanup Sweep

Goal: Remove deprecated, low-utility, or duplicate glossary terms

Tasks:
• CLI: audit_glossary_duplicates
• Detect anchors with identical or similar token values
• Flag anchors that:
• Are unused
• Have 0 hits or linked chunks
• Are shadowed by better scoring terms
• Suggest merges or mutations
• Show in SymbolicAnchorReviewPage tab

⸻

🔸 Ω.10.v — Anchor Reflection & Insight Logging

Goal: Reflect on every new glossary anchor to document what it represents

Tasks:
• Hook into anchor creation pipeline
• Run assistant-level reflection summarizing anchor purpose
• Save reflection as MemoryEntry and link it to anchor
• Expose anchor-insight chain in the anchor detail view

⸻

🔸 Ω.10.w — Anchor Utility Index

Goal: Score anchors by impact using weighted combination of usage, match score, and fallback behavior

Tasks:
• Add computed field: utility_score = avg_score _ usage_weight _ stability
• Display in UI and diagnostics
• Allow optional suppression below threshold (e.g., utility < 0.2)
• Track per-assistant usage counts and fallback rates

⸻

🔁 Recurring CLI Commands

These should be run weekly, or post-ingestion:

python manage.py run_rag_diagnostics --assistant=slug
python manage.py validate_anchors
python manage.py repair_anchor_recall
python manage.py relink_anchor_chunks
python manage.py sync_missing_diagnostics
python manage.py generate_diagnostic_reports

⸻

💡 Optional Ω.10.x — Anchor Feedback UI

Idea: Let users tag chunks during chat to flag whether a source was actually helpful.

Tasks:
• Add 👍/👎 or “Not Helpful” to retrieved chunk footer
• Log AnchorFeedbackLog with chunk, anchor, and response context
• Use this for future anchor mutation, scoring, or deletion

⸻

Next Step

Select which phase you want to execute next — Codex is standing by.

Recommended: Ω.10.t — RAG Recall Booster to begin strengthening glossary from known weak points.
