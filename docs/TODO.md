✅ TODO.md — Phase Ω.10.t → Ω.10.u

Last Updated: 2025-06-14
Context: Tracking all tasks spun up during Phase Ω.10.t — RAG Recall Booster, and prepping for Phase Ω.10.u — Symbolic Feedback Review Panel

⸻

🔥 ACTIVE PRIORITY — Ω.10.t: RAG Recall Booster

Backend
• Implement suggest_better_anchors CLI command
• Scan fallback matches in RAGGroundingLog and find nearby high-score chunks
• Extract token candidates, compare with current anchors
• Log suggestions as SymbolicMemoryAnchor mutations
• Add --auto-approve support
• Create regression/unit test for fallback-to-anchor suggestion flow
• Document command in AGENTS.md

Frontend (Pending)
• Add suggest_better_anchors to CLI Runner UI
• Add assistant dropdown + auto-approve toggle
• Show CLI output logs in scrollable panel

⸻

🧠 PREP PHASE — Ω.10.u: Symbolic Feedback Review Panel

Backend
• Add filterable views for:
• suggested anchors by assistant
• fallback frequency
• auto-approved vs pending
• Add endpoint to accept/reject/edit anchor suggestions

Frontend
• Create /anchor/suggestions route + UI panel
• Table: suggested term, source fallback, score context, linked chunk
• Accept / Reject / Edit actions with comment field
• Tie mutation actions to assistant glossary score feedback

⸻

⚙️ Infrastructure
• Run run_rag_diagnostics on all assistants (ongoing)
• Run rank_glossary_anchors_by_hits and log weakest anchors
• Audit inspect_embeddings for orphaned or broken chunks

⸻

✨ Codex-Ready Tasks
• Create ✅ Phase Ω.10.t — suggest_better_anchors.md
• Add output mutation viewer to /assistants/:slug/reflections/ (if missing)
• Add symbolic anchor hit chart to /assistants/:slug/rag_debug/

⸻

🧠 Notes for Future Review
• Revisit symbolic anchor mutations across sessions
• Track anchor usage and fallback recovery trends
• Prepare Recurra for contradiction analysis with updated anchors
