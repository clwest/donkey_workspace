# 🧠 Assistant Lifecycle Integration Checklist

Goal: Confirm that a single YouTube input can result in a fully functioning assistant with a linked prompt, project, objective, planned tasks, and agent assignments.

---

## ✅ Step 1: Ingest a YouTube Video

- [ ] `POST /api/intel/ingest` with `source_type: "youtube"` and a valid `url`
- [ ] Response includes a new `Document` with `id`, `title`, `summary`

---

## ✅ Step 2: Bootstrap Assistant from Document

- [ ] `POST /api/intel/bootstrap-agent-from-docs/<document_id>/`
- [ ] Assistant is created with:
  - [ ] Name, personality, tone, and linked system prompt
  - [ ] Linked to the ingested document
  - [ ] Initial project and objective created

---

## ✅ Step 3: Confirm Assistant Project & Objective

- [ ] `/api/assistants/` shows the assistant
- [ ] `/api/assistants/projects/` includes the linked project
- [ ] The project includes:
  - [ ] At least one `Objective`
  - [ ] Link to assistant and document

---

## ✅ Step 4: Plan Tasks from Objective

- [ ] `POST /api/assistants/<slug>/objectives/<id>/plan-tasks/`
- [ ] Returns task list
- [ ] `AssistantThoughtLog` created
- [ ] Tasks saved to project and linked to objective

---

## ✅ Step 5: Reflect + Assign Agents

- [ ] `POST /api/assistants/<slug>/reflect-thread/<thread_id>/`
- [ ] Assistant reflection returns `AssistantNextAction[]`
- [ ] Each NextAction has `agent_id` assigned

---

## Optional Bonus Checks

- [ ] Assistant memory updated with symbolic reflection after planning
- [ ] Project is visible in dashboard view
- [ ] Agents are visible in task plan or action list

---

If any step above fails, **note the break** and call `debug_lifecycle_flow()` on that part.
