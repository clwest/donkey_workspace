from assistants.models.project import (
    AssistantProjectRole,

)
from assistants.models.thoughts import CollaborationLog, AssistantThoughtLog
from project.models import Project


def evaluate_team_alignment(project_id):
    project = Project.objects.filter(id=project_id).first()
    if not project:
        return None

    roles = project.roles.select_related("assistant")
    assistants = [r.assistant for r in roles]

    moods = []
    for a in assistants:
        last = a.thoughts.order_by("-created_at").first()
        moods.append(getattr(last, "mood", "neutral"))
    mood_state = ",".join(moods)

    styles = [a.collaboration_style for a in assistants if a.collaboration_style]
    style_conflict = len(set(styles)) > 1

    log = CollaborationLog.objects.create(
        project=project,
        mood_state=mood_state,
        style_conflict_detected=style_conflict,
    )
    log.participants.set(assistants)
    return log


def detect_conflict_signals():
    return AssistantThoughtLog.objects.filter(
        mood__in=["frustrated", "angry"]
    ).order_by("-created_at")[:20]
