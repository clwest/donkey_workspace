from __future__ import annotations

from typing import List

from assistants.models.assistant import Assistant
from assistants.models.project import AssistantProject, AssistantObjective
from agents.models.core import Agent
from agents.utils.agent_controller import AgentController
from core.services.agent_service import spawn_agent_for_skill


def assign_agents_to_project_from_objective(
    assistant: Assistant, objective: str
) -> List[Agent]:
    """Create project + objective and assign recommended agents."""
    project, _ = AssistantProject.objects.get_or_create(
        assistant=assistant, title=objective
    )
    obj, _ = AssistantObjective.objects.get_or_create(
        assistant=assistant, project=project, title=objective
    )

    controller = AgentController()
    recommended: List[Agent] = []
    agent = controller.recommend_agent_for_task(
        objective, project.thread if hasattr(project, "thread") else None
    )
    if agent:
        recommended.append(agent)
    else:
        # spawn specialist if none available
        agent = spawn_agent_for_skill(objective, {"parent_assistant": assistant})
        recommended.append(agent)

    project.agents.set(recommended)
    return recommended
