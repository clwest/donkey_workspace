# v0.1 Demo Release – 2025-06-10

These notes summarize the features and fixes delivered across Phases 1–5 of the onboarding and tour initiative.

## Phase 1 – Onboarding Flow
- New `/assistants/onboarding` route with theme selector wizard
- Backend endpoint for assistant creation
- Links from landing page and navigation

## Phase 2 – First‑Use Tour
- Guided overlays highlight dashboard, memory, and glossary features
- Tour completion state stored per user
- Skip/Done option to disable on future logins

## Phase 3 – Self‑Learning Loop Setup
- "Reflect now" button added to chat sessions
- User feedback stored as `MemoryEntry`
- Reflection logs exposed at `/assistants/<slug>/reflections`

## Phase 4 – Demo Assistant Flows
- Trust profile view shows score and badges
- Trail timeline and growth panel track progress
- Recap, overlay, and replay pages for demo sessions

## Phase 5 – QA, Data Seeding & Performance
- End‑to‑end tests cover onboarding through replay
- `seed_all.sh` populates demo assistants and sessions
- Basic API benchmark script records first load latency

## Critical Fixes
- RAG debugging routes linked in navigation
- Glossary fallback catcher prevents blank prompts
- Seeders now idempotent to avoid duplicate data

---

For a full list of routes and models see the [API Overview](api_overview.md).
