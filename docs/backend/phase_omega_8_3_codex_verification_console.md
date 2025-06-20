# 🧠 Phase Ω.8.3 — Codex Verification Console + Route Linting Engine

## 🧭 Objective

Create a self-checking interface to **validate frontend routes, component bindings, and backend/frontend integration**. This ensures all Codex-generated routes are properly implemented, wired, and render as expected — catching blank pages, undefined components, and dead endpoints early.

---

## ⚠️ Problem Recap

- Codex creates routes and views rapidly
- Many frontend routes lead to blank or broken pages
- `/dev/routes` lists endpoints, but doesn't verify component health
- You have no fast way to confirm Codex changes *actually work*

---

## 🛠 Goals

### 🔹 1. Route Component Validator
- Create `/debug/route-audit`
- For each frontend route:
  - Attempt to import its target component
  - Attempt to shallow render
  - Report one of:
    - ✅ Valid (component renders)
    - ❌ Broken (component missing or throws)
    - ⏳ Pending (lazy component not yet loaded)

### 🔹 2. Enhanced `/dev/routes` Table
- Add a “Status” column for frontend routes:
  - ✅: Rendered OK
  - ❌: Missing import or undefined element
  - 🔍: Exists in router but not linked to a real page

### 🔹 3. Backend ↔ Frontend Mapper
- Create script to:
  - Extract all registered DRF routes (e.g. via `urlpatterns`)
  - Match each to corresponding frontend route (if one exists)
  - Show which APIs have no matching frontend
  - Show which frontend routes hit undefined or unused APIs

---

## 🔧 Dev Tasks

### Frontend
- [ ] Add `RouteAuditPanel.jsx` at `/debug/route-audit`
- [ ] Add component resolution checker for each frontend route
- [ ] Upgrade `/dev/routes` to reflect render status

### Backend
- [ ] Optional: script `lint_routes.py` to compare DRF URLConf to frontend paths

---

## 🧪 Verification

| Route | Expected |
|-------|----------|
| `/assistants/:id/chat` | ✅ Renders AssistantChatPage |
| `/assistants/:id/fork/replay` | ❌ Missing component |
| `/codex/evolve` | ✅ Component loads |
| `/codex/contracts/promptId` | 🔍 Exists in API but no frontend route |

---

## 🧠 Bonus Features

- [ ] Add last-touched Git commit info per route (via `git log`)
- [ ] Export “broken route report” to Codex or Markdown

---

## 🔁 Related Phases
- Ω.8.1 — RAG Debug + Source Audit
- Ω.8.2 — Assistant Document Assignment
- Phase X — Frontend Observability Layer

---

## 🧠 TL;DR:
> Codex writes fast. This console reads the truth.  
> A route without a working component is a ghost. Let’s name every one of them.