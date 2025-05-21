from __future__ import annotations

from typing import List

from agents.models import (
    Agent,
    AgentTrainingAssignment,
    AgentSkill,
)
from assistants.models import Assistant
from agents.models import AgentFeedbackLog
from agents.utils.agent_controller import recommend_training_documents
from intel_core.models import Document


def _skill_names(skills: list) -> List[str]:
    names = []
    for s in skills or []:
        if isinstance(s, dict):
            if s.get("skill"):
                names.append(s["skill"].lower())
        else:
            names.append(str(s).lower())
    return names


def build_adaptive_curriculum(
    agent: Agent, assistant: Assistant
) -> List[AgentTrainingAssignment]:
    """Return 2-4 training assignments based on skill gaps and project needs."""
    existing = set(_skill_names(agent.verified_skills))
    feedback_logs = AgentFeedbackLog.objects.filter(agent=agent).order_by(
        "-created_at"
    )[:5]

    feedback_skills = set()
    for log in feedback_logs:
        words = [w.strip(".,!").lower() for w in log.feedback_text.split()]
        for word in words:
            if (
                word not in existing
                and AgentSkill.objects.filter(name__iexact=word).exists()
            ):
                feedback_skills.add(word)

    related = set()
    for name in existing:
        try:
            skill_obj = AgentSkill.objects.get(name__iexact=name)
            related.update(
                skill_obj.related_skills.exclude(name__in=existing).values_list(
                    "name", flat=True
                )
            )
        except AgentSkill.DoesNotExist:
            continue

    desired = feedback_skills | {r.lower() for r in related}

    docs: List[Document] = list(recommend_training_documents(agent))
    if desired:
        docs_for_skills = Document.objects.filter(
            tags__name__in=list(desired)
        ).distinct()
        docs = list(docs_for_skills) + docs

    if assistant.projects.exists():
        docs += list(assistant.projects.first().documents.all())

    seen = set()
    ordered = []
    for d in docs:
        if d.id not in seen:
            seen.add(d.id)
            ordered.append(d)
        if len(ordered) >= 4:
            break

    assignments: List[AgentTrainingAssignment] = []
    for doc in ordered[:4]:
        assignments.append(
            AgentTrainingAssignment.objects.create(
                agent=agent,
                assistant=assistant,
                document=doc,
            )
        )

    return assignments
