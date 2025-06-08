from django.utils import timezone
from assistants.models import Assistant
from assistants.models.project import AssistantObjective, AssistantMemoryChain
from assistants.models.reflection import AssistantReflectionLog


def get_nurture_recommendations(assistant: Assistant) -> list[str]:
    """Return suggested next steps for nurturing a new assistant."""
    recs = []
    if not AssistantReflectionLog.objects.filter(
        assistant=assistant, title="Origin Reflection"
    ).exists():
        recs.append("reflect_birth")
    if not AssistantObjective.objects.filter(assistant=assistant).exists():
        recs.append("create_first_objective")
    if not AssistantMemoryChain.objects.filter(team_members=assistant).exists():
        recs.append("start_memory_chain")
    return recs
