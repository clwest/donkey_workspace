# Agent

## Models

### Agent

    - name
    - slug
    - description
    - agent_type
    - preferred_llm
    - execution_mode
    - parent_assistant (fk, assistants.Assistant)
    - created_at
    - updated_at

### AgentThought

    - agent (fk Agent)
    - input_text
    - response_text
    - reasoning
    - error_message
    - tags (Currently ArrayField, needs to be fk I think)
    - created_at
    - updated_at

## Utils/agent_controller.py

    - AgentController:
    - reflect()
    - create_plan()
    - create_task()
    - assign_agent()
    - log_action()
    - think_with_agent()
    - chat_with_agent()
    - log_thought()

## Utils/agent_reflection_engine.py

    - AgentReflectionEngine:
    - reflect_on()
    - summarize_reflection()
    - get_llm_summary()
    - get_structured_reflection()
    - analyze_mood()
    - reflect_on_custom()
    - expand_summary()
    - generate_reflection_title()
    - get_llm_summary_from_raw_summary()

## Utils/debugger_agent.py

    - DebuggerAgent:
    - find_open_faults()
    - suggest_debugging_agent()
    - dashboard_debug_summary()

## Views/agents.py

    - list_agents()
    - agent_detail_view()

### serializers.py

    AgentSerializer

### urls.py

    - "/"
    - <slug:slug>/
