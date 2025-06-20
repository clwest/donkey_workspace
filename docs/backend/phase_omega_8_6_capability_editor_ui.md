# 🧠 Phase Ω.8.6 — Assistant Capability Editor UI

## 🧭 Objective

Create a dedicated UI for viewing and editing an assistant’s capabilities, enabling real-time configuration of feature access such as Glossary Training, Reflections, Delegation, RAG permissions, and more.

This phase gives devs and users the ability to **toggle abilities per assistant**, replacing the need for hardcoded defaults or slug-based logic.

---

## 🛠 Goals

### 🔹 1. Assistant Capability Panel
- Add new route: `/assistants/:slug/capabilities`
- Render form with:
  - Toggle switches for:
    - ✅ `can_train_glossary`
    - ✅ `can_run_reflection`
    - ✅ `can_delegate_tasks`
    - ✅ `can_ingest_docs`
    - ✅ `can_embed`
    - ✅ `can_self_fork`
  - JSON preview panel to show current values

### 🔹 2. Save to Assistant Model
- PATCH updates to Assistant’s `capabilities` field
- Backend should accept either full JSON object or patch dict

### 🔹 3. Optional: Admin Overlay
- Add “⚙️ Edit Capabilities” button to Assistant Overview Page
- Button links to `/assistants/:slug/capabilities`

---

## 🔧 Dev Tasks

### Backend
- [ ] Ensure Assistant model has `capabilities = JSONField(default=dict)`
- [ ] Expose `capabilities` in Assistant serializer (read+write)
- [ ] Accept PATCH updates via `/api/assistants/:id/`

### Frontend
- [ ] Create `AssistantCapabilityEditor.jsx`
- [ ] Add route `/assistants/:slug/capabilities`
- [ ] Render toggle form, update via API
- [ ] Add edit button on `/assistants/:slug` detail page

---

## 🧪 Verification

| Action | Expected |
|--------|----------|
| Toggle “can_train_glossary” → false | Glossary tab hidden from UI |
| Toggle “can_run_reflection” → true | Reflection tools reappear |
| Save update → reload assistant | Capabilities reflected in dashboard |

---

## 🔁 Related Phases
- Ω.8.5 — Capability Model Patch
- Ω.8.2 — Document Assignment System
- Ω.8.1 — Anchor + Reflection Engine

---

## 🧠 TL;DR:
> Assistants evolve through belief, memory, and role.  
> This UI gives them a switchboard for capability — and you a way to govern their power.