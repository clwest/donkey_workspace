# Assistant-related Views in assistants/views/assistant.py

## Endpoints Overview

### List and Create Assistants

- **URL**: `/api/assistants/`
- **Methods**: `GET`, `POST`
- **Views**: `assistants_view`
- **Frontend**: `/assistants` (list), `/assistants/create` (form)

### Assistant Detail View

- **URL**: `/api/assistants/<slug>/`
- **Method**: `GET`
- **View**: `assistant_detail_view`
- **Frontend**: `/assistants/:slug`

### Create from Thought

- **URL**: `/api/assistants/from_thought/`
- **Method**: `POST`
- **View**: `create_assistant_from_thought`
- **Frontend**: used via planning flows / AI reflections

### Chat with Assistant

- **URL**: `/api/assistants/<slug>/chat/`
- **Method**: `POST`
- **View**: `chat_with_assistant_view`
- **Frontend**: `/assistants/:slug/chat`

### Flush Session to Memory

- **URL**: `/api/assistants/<slug>/flush/`
- **Method**: `POST`
- **View**: `flush_chat_session`
- **Frontend**: automatic from chat components

### Demo Assistants

- **URL**: `/api/assistants/demos/`
- **Method**: `GET`
- **View**: `demo_assistant`
- **Frontend**: `/assistants-demos`

### Reflect on Assistant

- **URL**: `/api/assistants/thoughts/reflect_on_assistant/`
- **Method**: `POST`
- **View**: `reflect_on_assistant`
- **Frontend**: potentially `/assistants/:slug/reflect` or system tools

---

## ForeignKey & Related Models

- `Assistant.system_prompt -> prompts.Prompt`
- `AssistantThoughtLog.assistant -> assistants.Assistant`
- `AssistantThoughtLog.project -> project.Project`
- `Assistant.created_by -> auth.User`

## Utility Dependencies

- `assistant_session.py`: chat message handling (save/load/flush)
- `assistant_thought_engine.py`: logs chain-of-thought traces
- `memory_helpers.py`: creates `MemoryEntry`
- `logging_helper.py`: logs assistant-generated thoughts

Let me know when you’re ready to map the next view file or add new frontend routes for these!
