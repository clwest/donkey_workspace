Proposed Demo-Readiness Workflow

Phase 1: Onboarding Flow
Objective: Guide new users through creating their first assistant using a theme-based wizard.

Deliverables:

/assistants/onboarding route with theme selector UI

Backend endpoint for assistant creation

Links from landing page and nav

Key Tasks:

Implement the onboarding form and templates

Register the new route in App.jsx as required by AGENTS protocol

Seed starter assistants so the flow can be demoed quickly

Phase 2: First‑Use Tour
Objective: Show users the main features right after onboarding.

Deliverables:

Guided overlays for Dashboard, Memory, and Glossary pages

“Skip/Done” state saved to user profile

Key Tasks:

Integrate a tour library (e.g., react‑joyride)

Define steps that highlight the trust profile, trail timeline, and growth panel routes noted in the recap

Add settings flag to disable the tour after completion

Phase 3: Self‑Learning Loop Setup
Objective: Enable assistants to reflect on user feedback and improve.

Deliverables:

“Reflect now” button on chat sessions

Memory entries storing user feedback

Trigger for automated reflections

Key Tasks:

Create a CTA on session pages that saves feedback as MemoryEntry

Invoke reflection routines using the existing reflection APIs

Expose reflection logs through the /assistants/:slug/reflections route from the dashboard list

Phase 4: Demo Assistant Flows
Objective: Polish demo-related screens showing trust, trail, and growth metrics.

Deliverables:

Trust profile view with score and badge counts

Trail timeline with milestone summaries

Growth panel tracking stage progress

Recap, overlay, and replay pages for demo sessions

Key Tasks:

Ensure each panel is reachable via buttons or nav, per AGENTS rules

Display boosted prompt metadata in overlay/recap screens

Hook up logging for DemoUsageLog and DemoSessionLog

Phase 5: QA, Data Seeding & Performance
Objective: Validate the full flow and prepare sample data.

Deliverables:

End‑to‑end tests covering onboarding through demo replay

seed_all.sh integration for demo assistants and example sessions

Basic performance benchmarks for first load and reflection requests

Key Tasks:

Extend existing test scripts to cover each new route

Automate seeding of starter assistants and demo sessions

Profile API calls to ensure demo smoothness

Phase 6: Documentation & Demo Prep
Objective: Finalize user‑facing docs and craft a demo script.

Deliverables:

Updated README and quick‑start guide

Slide deck or short screencast for presenters

Checklist for live demo run‑through

Key Tasks:

Summarize the assistant system, referencing the route map and architecture docs

Document the onboarding tour and self‑learning features

Prepare sample flows showing trust profile and growth progress

This phased approach brings the onboarding, tour, self‑learning loop, and demo analytics online, then wraps up with QA and documentation so the system is ready for users to try.
