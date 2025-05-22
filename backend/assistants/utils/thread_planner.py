from assistants.models.project import AssistantNextAction
from agents.models.core import AgentFeedbackLog
from agents.utils.agent_controller import update_agent_profile_from_feedback


def plan_from_thread_context(thread):
    """Return next actions for a thread and log feedback results."""
    actions = AssistantNextAction.objects.filter(thread=thread)
    for action in actions:
        result = getattr(action, "result", None)
        agent = getattr(action, "assigned_agent", None)
        if result and agent:
            log = AgentFeedbackLog.objects.create(
                agent=agent,
                task=action,
                feedback_text=result,
                feedback_type="result",
            )
            update_agent_profile_from_feedback(agent, [log])
    return list(actions)
