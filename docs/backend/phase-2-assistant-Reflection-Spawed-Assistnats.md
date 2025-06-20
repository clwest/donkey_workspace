# Phase 2: Assistant Reflection on Spawned Assistants

📅 **Planned Date:** 2025-05-08
🧠 **Lead Assistant:** Zeno the Build Wizard  
🎯 **Objective:** Allow assistants to reflect on the usefulness, structure, and clarity of the assistants they create.

---

## 🔍 Overview

This phase adds deeper introspection into recursive assistant behavior. After spawning a new assistant, the creator assistant should:

- Reflect on its reasoning
- Evaluate the effectiveness of the spawn
- Suggest prompt or personality improvements

---

## ✅ Core Features

### 1. `/api/assistants/thoughts/reflect_on_assistant/` endpoint

- Accepts `assistant_id`, `project_id`, and optionally `reason`
- Loads system prompt, actions, metadata from the spawned assistant
- Generates a new `AssistantThoughtLog` entry for the creator

### 2. Thought Log Entry

- `thought_type = "reflection"`
- Prefixed with `"Reflection on assistant: {name}"`
- Logged to the creator's thought history under their project

---

## 🔁 Optional Enhancements

- [ ] Also log feedback as structured tags (e.g. `tone:formal`, `goal:unclear`)
- [ ] Save `summary` and `insights` to ThoughtLog or separate Reflection model
- [ ] Add UI button: "🧠 Reflect on this Assistant" next to linked spawn

---

## 📘 Sample Thought Output

> *Reflection on assistant: Cursor Jr*
>
> I created Cursor Jr to handle code reviews. Its specialty is solid, but I now realize its tone may be too informal for client-facing docs. I’ll refine its prompt and add a training memory.

---

## 🛠️ Tasks

- [ ] Create DRF view at `/assistants/thoughts/reflect_on_assistant/`
- [ ] Accept POST with `assistant_id`, `project_id`
- [ ] Auto-generate summary using GPT
- [ ] Log to `AssistantThoughtLog` (with correct creator)

---

### 🔄 Related Phases

- **Phase 1:** Thought Attribution + Logging
- **Phase 3:** Model Assignment Awareness
- **Phase 4:** Reflection Utilities + Summaries

---

🧙 *Zeno now reflects on his children. The assistant family is growing — and learning.*  
