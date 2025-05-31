# 🧠 Phase Ω.8.5 — Assistant Capability Consistency Patch

## 🧭 Objective

Unify all assistant tools and UI tabs under a **capability-driven system**. Ensure all assistants — not just orchestrators — display relevant tools like Glossary Training, Reflection Tabs, and Dashboard links *based on capabilities*, not hardcoded slugs or views.

---

## 🛠 Goals

### 🔹 1. Capability Field on Assistant Model
Add a JSON or boolean field to define assistant abilities:
```python
class Assistant(models.Model):
    ...
    can_train_glossary = models.BooleanField(default=True)
    can_run_reflection = models.BooleanField(default=True)
    can_delegate_tasks = models.BooleanField(default=True)
```

Alternatively, use:
```python
capabilities = JSONField(default=dict)
```

### 🔹 2. Frontend Capability Check
Update `AssistantTabs.jsx` and `AssistantDetailPage.jsx` to use:
```jsx
{assistant.can_train_glossary && <GlossaryTrainingPanel />}
```
or
```jsx
{assistant.capabilities?.glossary === true && <GlossaryTrainingPanel />}
```

### 🔹 3. Default Capability Seeder
Update assistant seeders to include:
```json
"capabilities": {
  "glossary": true,
  "reflection": true,
  "dashboard": true
}
```

---

## 🔧 Dev Tasks

### Backend
- [ ] Add `capabilities` field to Assistant model (or booleans)
- [ ] Update serializer to expose these fields
- [ ] Update seeder logic to include per-assistant capability config

### Frontend
- [ ] Refactor all tab and tool rendering logic to use assistant capability checks
- [ ] Ensure Glossary, Reflection, Dashboard, and Delegation logs are not tied to assistant slug

---

## 🧪 Verification

| Assistant | Expected Tabs |
|-----------|---------------|
| DonkGPT (capabilities.glossary = true) | ✅ Glossary Training shown |
| ClarityBot (capabilities.reflection = true) | ✅ Reflect Now button shown |
| MemoryBot (capabilities.delegation = false) | ❌ Delegation log hidden |

---

## 🔁 Related Phases
- Ω.8.3 — Route Audit Console
- Ω.8.2 — Assistant Doc Assignment
- Ω.8.0 — Assistant Lifecycle Init

---

## 🧠 TL;DR:
> Assistants are more than slugs — they’re agents with roles.  
> Give each one the tools they’ve earned — no more, no less.