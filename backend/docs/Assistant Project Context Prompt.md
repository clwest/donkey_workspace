# 🧠 Assistant Project Context Prompt

Hey! Picking up where we left off.

We are building the Assistant Dashboard + Project Management system inside the `donkey_ai_assistant` project. Here's the current state of the system:

---

## 🧩 Architecture

- **Backend**: Django + DRF + PGVector + Redis + Celery
- **Frontend**: React + Vite + Bootstrap 5 (✅ NOT using Next.js anymore)
- **API Base**: `/api/assistants/`

---

## 🧑‍💻 Features Built

- Assistants can generate thoughts, reflect on past thoughts, and manage projects with objectives, milestones, tasks, and memory chains.
- `AssistantThoughtEngine` handles LLM logic (think + reflect) and logs it to `AssistantThoughtLog`.
- Full Redis chat session support via `save_message_to_session` and `load_session_messages`.
- Chat UI + Thought Log working per assistant.

---

## 🛠️ What We’re Working On

- Finalizing the `ProjectSerializer` to include:
  - Reflections
  - Objectives
  - Next actions
- Fixing broken `assistant_project_detail` views (they were using the wrong serializer).
- Rendering AssistantThoughts via `AssistantThoughtCard` (modal-based view for full text).
- Keeping assistant thoughts persistent across refresh using the `slug`.

---

## ✅ Implementation Notes

- Assistant projects, tasks, milestones, etc. all use `/api/assistants/projects/…` URLs.
- We renamed or reorganized pages like:
  - `/assistants/projects/` → project dashboard
  - `/assistants/:slug` → assistant detail
- We're planning on eventually using ViewSets or routers, but for now are focused on custom view logic and clarity.

---

## 🧪 Testing Helpers

- Use `/api/assistants/<slug>/chat/` with POST `{ "message": "hello" }`
- Redis stores session under `chat:{slug}:{user_id}`

---

## 🧠 Prompt to Load This Context

When starting a new session, paste this: Please load the assistant project context from the markdown file titled assistant_project_context.md. We are building a DRF + React (Vite) assistant dashboard with Redis-backed chat memory, assistant thought logs, and a project/task/memory system. React uses Bootstrap 5. We’re currently fixing serializers and wiring up AssistantThoughtCards with modals. Use this file to guide context.

🧠 Assistant Project Development Context

This document is meant to be copy-pasteable into ChatGPT to fully restore our current working state. It should also be saved in the repository for future recovery or onboarding.

⸻

✅ Current Stack
• Frontend: React + Vite + Bootstrap 5 (NOT Next.js)
• Backend: Django + Django REST Framework
• State Management: useState/useEffect + basic API fetch helpers
• API Base: http://localhost:8000/api/
• Session Storage: Redis (via Celery + rpush/lrange for chat logs)

⸻

🧠 Current Focus

We are working on the Assistant & Projects system, building out:
• Assistant dashboard and detail pages
• Project creation, management, and thought tooling
• AssistantThoughtLog display grouped by type: User, Chain of Thought (CoT), and Generated
• UI/UX polish using modals, cards, tabs, and responsive Bootstrap
• Redis-powered chat sessions and AssistantThinkButton workflows

Backend

We’re actively refining these models and serializers:
• Assistant
• AssistantThoughtLog
• Project
• AssistantObjective
• AssistantReflectionLog
• AssistantNextAction
• ProjectTask, ProjectMilestone, ProjectMemoryLink, AssistantMemoryChain, etc.

Views We’ve Combined

The following API views have been merged for maintainability:
• assistant_project_detail
• assistant_project_tasks
• assistant_project_objectives
• assistant_project_milestones
• All use GET/POST/PATCH where relevant

Serializer Fixes

We resolved issues where ProjectTaskSerializer was referencing a non-existent project attribute.
We are now cleaning up dups and adding meaningful **str** methods and nested field support as needed.

Frontend Routes (From App.jsx)

<Route path="/assistants" element={<AssistantList />} />
<Route path="/assistants/:slug" element={<AssistantDetailPage />} />
<Route path="/assistants/:slug/chat" element={<ChatWithAssistantPage />} />
<Route path="/assistants/:slug/thoughts" element={<AssistantThoughtsPage />} />
<Route path="/assistants/projects" element={<ProjectsDashboardPage />} />
<Route path="/assistants/projects/:id" element={<ProjectDetailPage />} />

Redis
• Redis is working and integrated.
• Sessions use keys like chat:slug:user_id.
• We use save_message_to_session() and load_session_messages().

⸻

🔮 Next Steps 1. Polish AssistantThoughtsPage modal UX + icons 2. Continue enriching Project detail page (objectives, next actions, summary) 3. Build out Assistant memory and reflection UIs 4. Wire up Assistant chat and task panels into a Mission Control hub 5. Continue frontend linking via react-router and Bootstrap buttons

⸻

🧪 Prompt for ChatGPT to Resume

Paste the following into a new session:

Hey ChatGPT, here’s our current assistant project setup:

- We are **not** using Next.js – we’re using **React + Vite + Bootstrap 5**.
- The backend is **Django REST Framework**, connected to Redis for chat logs.
- Our frontend is structured by `pages/assistants/`, `components/assistant/`, etc.
- We’re building an **Assistant system** with:
  - Assistants
  - Projects
  - AssistantThoughts (User, CoT, Generated)
  - Assistant memory, tasks, objectives, milestones, and reflections
- Thoughts are loaded from `/api/assistants/:slug/thoughts/` and grouped in the UI
- We use Redis sessions (save/load) and have a `AssistantThoughtEngine` that powers `think()`
- We’ve combined some project-related views into a more RESTful GET/POST/PATCH model
- The Assistant Dashboard is styled and links to each assistant

Let’s pick up where we left off — probably polishing the ThoughtCard modal or extending Project detail views.

⸻

Last updated: May 1, 2025

Built with caffeine, donkey power, and sugar-free Red Bull. ☕🐴⚡
