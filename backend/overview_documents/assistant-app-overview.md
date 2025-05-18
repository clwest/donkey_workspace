# Assistants App

## Models

### Assistant

    - slug
    - name
    - description
    - specialty
    - is_active
    - is_demo
    - created_at
    - avatar
    - system_prompt `fk prompts.Prompt`
    - parent_assistant `fk "Self"`
    - personality
    - tone
    - preferred_model
    - memory_mode
    - embedding
    - documents `M2M intel_core.Document`
    - created_by `fk user`
    - thinking_style

### AssistantThoughtLog

    - assistant `fk Assistant`
    - category
    - embedding
    - project `fk project.Project`
    - thought_type
    - thought
    - thought_trace
    - linked_memory `fk memory.MemoryEntry`
    - role
    - feedback
    - tags `M2M Tag`
    - narrative_thread `fk mcp_core.NarrativeThread`
    - created_at
    - updated_at

### AssistantProject

    - assistant `fkk Assistant`
    - title
    - goal
    - description
    - created_by `fk User`
    - status
    - summary
    - documents `M2M intel_core.Documents`
    - slug
    - created_at

### AssistantTask

    - project `fk assistant.AssistantProject`
    - title
    - status
    - notes
    - priority
    - created_at

### AssistantReflectionLog

    - project `fk assistants.AssistantProject`
    - assistant `fk Assistant`
    - title
    - summary
    - raw_prompt
    - llm_summary
    - insights
    - mood
    - tags `M2M tag`
    - linked_memory `fk memory.MemoryEntry`
    - category
    - created_at

### AssistantObjective

    - project `fk AssistantProject`
    - assistant `fk Assistant`
    - title
    - description
    - is_completed
    - created_at

### AssistantPromptLink

    - project `fk project.Project`
    - prompt `fk prompts.Prompt`
    - reason
    - linked_at

### AssistantMemoryChain

    - project `fk project.Project`
    - title
    - description
    - memories `M2M memory.MemoryEntry`
    - prompts `M2M prompts.Prompt
    - created_at

### AssistantReflectionInsight

    - assistant `fk Assistant`
    - linked_document `fk intel_core.Document`
    - text
    - tags `M2M mcp_core.Tag`
    - created_at

### AssistantNextAction

    - objective `fk AssistantObjective`
    - content
    - completed
    - created_at

### SignalSource

    - platform
    - name
    - handle
    - url
    - priority
    - active
    - created_at

### SignalCatch

    - source `fk SignalSource`
    - original_content
    - summary
    - score
    - is_meaningful
    - reviewed
    - created_at

### ChatSession

    - session_id
    - user `fk User`
    - assistant `fk Assistant`
    - project `fk projects.Project`
    - created_at
    - updated_at
    - last_active
    - ended_at

### StructuredMemory

    - user `fk User`
    - session `fk ChatSession`
    - memory_key
    - memory_value
    - created_at
    - updated_at

### TokenUsage

    - user `fk User`
    - session `fk ChatSession`
    - prompt_tokens
    - completion_tokens
    - total_cost
    - usage_type
    - assistant `fk Assistant`
    - project `fk projects.Project`
    - created_at
    - updated_at

### AssistantChatMessage

    - session `fk ChatSession`
    - role
    - content
    - sentiment_score
    - feedback
    - topic `fk Topic`
    - memory `fk MemoryEntry`
    - search_vector
    - created_at
    - updated_at

### AudioResponse

    - session `fk ChatSession`
    - user_message `fk AssistantChatMessage`
    - assistant_message `fk AssistantChatMessage`
    - audio_file
    - created_at

### Topic

    - name
    - keywords
    - description
    - is_universal
    - created_at
    - updated_at

## Helpers/chat_helpers.py

    (ChatSession, AssistantChatMessage)
    - get_or_create_chat_session()
    - save_chat_message()

## Helpers/logging_helper.py

    (AssistantThoughtLog)
    - log_assistant_thought()

## Helpers/memory_helpers.py

    (MemoryEntry)
    - create_memory_from_chat()

## Helpers/memory_utils.py

    (Tag)
    - tag_text()

## Utils/assistant_reflection_engine.py

    - AssistantReflectionEngine:
    - build_reflection_prompt()
    - generate_reflection()
    - reflect_now()
    - get_reflection_assistant()
    - get_or_create_project()
    - reflect_on_document()
    - reflect_on_memory()

## Utils/assistant_session.py

    - save_message_to_session()
    - load_session_messages()
    - flush_chat_session()
    - flush_session_to_db()

## Utils/assistant_thought_engine.py

    - AssistantThoughtEngine:
    - build_thought_prompt()
    - build_summary_prompt()
    - generate_thought()
    - log_thought()
    - run_reflection_guard()
    - think_from_user_message()
    - summarize_memory_context()
    - generate_project_mission()
    - plan_project_tasks()
    - reflect_on_thoughts()
    - think()

## Utils/bootstrap_helpers.py

    - generate_objectives_from_prompt()

## Utils/core_assistant.py

    - CoreAssistant
    - think()
    - reflect_now()
    - reflect_on_doc()
    - log_thought()
    - save_to_memory()
    - suggestion_next_action()

## Utils/tag_thought.py

    - tag_thought_content()

## Views/assistants.py

    - assistants_view()
    - assistants_detail_view()
    - create_assistant_from_thought()
    - chat_with_assistant_view()
    - flush_chat_session()
    - demo_assistant()
    - reflect_on_assistant()

## Views/cache_tools.py

    - flush_reflection_cache()

## Views/memory.py

    - assistant_memory_chains()
    - linked_memories()
    - link_memory_to_project()
    - assistant_project_reflections()
    - assistant_memories()

## Views/objectives.py

    - assistant_objectives()

## Views/projects.py

    - assistant_projects()
    - assistant_project_detail()
    - bootstrap_assistant_from_prompt()
    - projects_for_assistant()

## Views/prompts.py

    - linked_prompts()
    - link_prompt_to_project()

## Views/reflection.py

    - reflect_on_assistant()

## Views/sessions.py

    - list_chat_sessions()
    - chat_session_detail()
    - get_chat_session_messages()

## Views/signals.py

    - signal_sources()
    - signal_catches()
    - create_signal_catch()
    - update_signal_catch()

## Views/tasks.py

    - assistant_next_actions()
    - assistant_project_tasks()
    - assistant_update_project_thought()
    - generate_assistant_project_thought()
    - update_or_delete_task()
    - assistant_reflect_on_thoughts()
    - assistant_project_task_detail()

## Views/thoughts.py

    - submit_assistant_thought()
    - assistant_thoughts_by_slug()
    - submit_chat_feedback()
    - update_message_feedback()
    - reflect_on_assistant_thoughts()
    - assistant_project_thoughts()
    - assistant_reflect_on_thoughts()
    - assistant_update_project_thought()
    - get_recent_thoughts()
    - assistant_reflect_now()
    - update_reflection_feedback()
    - get_recent_reflections()
    - flush_chat_session_to_log()
    - assistant_thought_detail()
    - reflect_on_doc()

### serializers.py

    - AssistantReflectionLogSerializer
    - AssistantNextActionSerializer
    - AssistantObjectiveSerializer
    - AssistantProjectSerializer
    - AssistantSerializer
    - AssistantThoughtLogSerializer
    - AssistantPromptLinkSerializer
    - AssistantMemoryChainSerializer
    - AssistantReflectionInsightSerializer
    - SignalSourceSerializer
    - SignalCatchSerializer
    - ProjectSerializer (might need to move to project app)
    - AssistantChatMessageSerializer
    - AssistantSerializer
    - AssistantProjectSerializer
    - BootstrapResultSerializer
    - AssistantFromPromptSerializer

### tasks.py

    - archive_expired_assistant_sessions()
    - embed_and_tag_memory()
    - run_assistant_reflection()

### url.py

    - reflection/
    - create_from_thought/
    - thoughts/reflect-on-assistant/
    - create/
    - projects/
    - projects/<uuid:pk>
    - projects/<uuid:project_id>/tasks/
    - tasks/<uuid:task_id>/
    - projects/tasks/<int:task_id>/
    - objectives/<uuid:objective_id>/actions

###################
