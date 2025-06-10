# 🎯 GOALS.md — Donkey Workspace Plan for 2025-06-06

This is the day’s tactical focus, following up on RAG mutation, glossary reflection, and Codex wiring.

---

## ✅ Review Summary from 2025-06-05

### What We Accomplished:

- RAG reflection replay CLI (`replay_reflections`) runs and logs changes
- Glossary mutation suggestions can now be accepted from the UI
- Mutation flow fixed with `suggested_label` syncing and anchor boost logging
- SymbolicGlossaryAnchor metadata enriched with:

  - `assistant`, `fallback_score`, `suggested_label`, `mutation_source`, `related_anchor`

- Assistant detail now links to:

  - `/replays/`, `/anchor/mutations`, `/anchor/symbolic`

- Anchor reinforcement logging added to track positive glossary term alignment

---

## 🚀 Today's Key Goals (Phase Ω.9.47+)

### 🧠 Phase Ω.9.47 — Reflection Drift Inspector

- [ ] Build a diff view for original vs replayed reflections
- [ ] Show term matches/losses (glossary anchors before/after)
- [ ] Tag score delta (summary shift due to replay)
- [ ] Let user mark a reflection as "drifted" or "stabilized"

### 🔁 Replay Feedback + Drift Controls

- [ ] Add Accept/Revert option to reflection replays
- [ ] Add reasoning tag: "Why did reflection change?"
- [ ] Allow mutation suggestions from drifted phrases

### 🗂️ Assistant Glossary Panel Cleanup

- [ ] Add filtering by status: `pending`, `applied`, `rejected`
- [ ] Show fallback count in table
- [ ] Style anchor label vs. suggested label with visual diff

### 🛠️ Dev Tools & Testing

- [ ] Add a CLI to list replay logs by assistant
- [ ] Add `/dev/replays/summary` route with per-assistant diff summary
- [ ] Ensure all `/replays/` pages are indexed in `App.jsx` and the nav

---

## 📎 Optional Stretch Goals

- [ ] Add glossary drift chart per assistant
- [ ] Create Codex panel to view all glossary feedback by term
- [ ] Let assistants propose mutation campaigns based on reflection replays

## 📝 User Feedback
- [ ] (bug) Overlay error when anchors undefined (demo)
- [ ] (idea) Add loading spinner on recap views (demo)
- [ ] (bug) Tour button misaligned on mobile (demo)

Save this as `GOALS.md` at the project root. These goals will guide Codex and UI routing work today.
