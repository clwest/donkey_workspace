📘 Phase 2 Roadmap — Donkey AI Assistant

This roadmap outlines our prioritized development goals for Phase 2, focusing on deepening the assistant’s core logic and laying the foundation for advanced input like signal monitoring.

⸻

✅ 1. Reflections Layer Polish
• Finalize AssistantReflectionLog write support
• Enable reflection creation from:
• Thought logs
• Completed/failed tasks
• Recent memory additions
• Add front-end reflection panel with write + summary preview
• Support project-level reflection roll-ups

⸻

✅ 2. Thought–Reflection–Objective Bridge
• Let thoughts suggest:
• New Objectives
• Suggested Tasks or Milestones
• Add UI option: “Convert to Objective/Task”
• Add backend support for tagging thoughts as goal-related

⸻

✅ 3. Memory Chain Structuring
• Enable grouped memory views by theme/subject
• Let user link memories manually + auto-clustering
• Visual timeline or chain view UI component
• Add memory importance rating + semantic proximity highlight

⸻

✅ 4. Auto-Prioritization System
• Add importance, urgency, and impact to:
• Tasks
• Objectives
• Reflections
• Smart sort logic for dashboard views
• Auto-ranking of incoming thoughts + tasks based on relevance
• Add visual weight indicator (e.g., 🔥 priority heat)

⸻

✅ 5. Signal Intelligence System (End of Phase 2)
• Finalize models:
• SignalSource
• SignalCatch
• Add viewsets, serializers, and API endpoints
• Build Agent or mock polling mechanism for select sources
• Support:
• Meaning detection (“Is this relevant?”)
• Convert to Thought
• Link to related memory/objective
• Create Signal Intelligence Panel in dashboard

⸻

⚙️ Supporting Tasks
• Prompt inference + embedding polish
• Improved navigation keyboard bindings (Raycast / Warp)
• Simplified project/module switching from command palette
• Docs & tooltips for every panel/component (low-hanging polish)

⸻

🔁 Daily Loop Enhancements
• Morning: reflect + prioritize
• Midday: task adjustment & context refresh
• Evening: review thoughts + seed reflections
• All tracked in /projects/:id view

⸻

Let me know if you’d like version tags (v2.1, 2.2…) or to sync this with a database model later!
