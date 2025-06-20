## Assistant App Overview (Inventory Dump)

### models.py

- **Assistant** ✅
- **Project** ✅
- **AssistantThoughtLog** ✅
- **AssistantReflectionLog** ✅
- **AssistantObjective** ✅
- **AssistantPromptLink** ✅
- **AssistantMemoryChain** ✅
- **AssistantReflectionInsight** ✅
- **AssistantNextAction** ✅
- **ProjectTask** 🔄 (May overlap with AssistantObjective)
- **ProjectMilestone** 🔄 (Needs review — milestone or duplicate of task?)
- **ProjectMemoryLink** 🔄
- **SignalSource** 🤷 (Unclear current role)

---

### utils/agent_reflection.py

- **AgentReflectionEngine (class)** ✅

  - `reflect_on()` ✅
  - `summarize_reflection()` ✅
  - `get_llm_summary()` ✅
  - `get_structured_reflection()` ✅

---

### utils/assistant_session.py

- `save_message_to_session()` ✅ Redis
- `load_session_messages()` ✅ Redis
- `flush_chat_session()` ✅ Redis
- `flush_session_to_db()` 🔄 Maybe deprecated now that we're embedding each message

---

### utils/assistant_thought_engine.py

- **AssistantThoughtEngine (class)** ✅

  - `think()` ✅
  - `generate_summary()` ✅
  - `summarize_project_state()` ✅
  - `reflect_on_thoughts()` ✅
  - `generate_project_mission()` ✅
  - `plan_project_tasks()` ✅

---

### tasks.py

- `archive_expired_assistant_sessions()` 🔄 (Not wired to Celery yet?)

---

### views.py

- `assistants_view()` ✅
- `assistant_projects()` ✅
- `assistant_project_details()` ✅
- `assistant_detail_view()` ✅
- `assistant_project_tasks()` ✅
- `assistant_project_task_detail()` ✅
- `update_or_delete_task()` ✅
- `generate_assistant_project_thought()` ✅
- `log_assistant_thought()` ✅
- `assistant_project_thoughts()` ✅
- `submit_assistant_thought()` ✅
- `assistant_thoughts_by_slug()` ✅
- `reflect_on_assistant_thoughts()` ✅
- `assistant_reflect_on_thoughts()` ✅
- `assistant_update_project_thought()` ✅
- `generate_project_mission()` ✅
- `ai_plan_project()` ✅
- `link_prompt_to_project()` ✅
- `link_memory_to_project()` ✅
- `linked_memories()` ✅
- `assistant_memory_chains()` ✅
- `assistant_reflection_insights()` ✅
- `assistant_objectives()` ✅
- `assistant_next_actions()` ✅
- `signal_sources()` 🤷
- `signal_catches()` 🤷
- `create_signal_catch()` 🤷
- `update_signal_catch()` 🤷

---

Let me know when you're ready and I can break this down into a visual map.
