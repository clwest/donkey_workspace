from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import CustomUser
from assistants.models.assistant import Assistant, ChatSession, AssistantChatMessage
from assistants.models.project import AssistantProject
from project.models import Project, ProjectType, ProjectStatus

@receiver(post_save, sender=CustomUser)
def create_personal_assistant(sender, instance, created, **kwargs):
    if not created or instance.personal_assistant:
        return
    assistant = Assistant.objects.create(
        name=instance.assistant_name or "Assistant",
        description="Personal assistant for user",
        specialty="general support",
        personality=instance.assistant_personality or "helpful",
        created_by=instance,
    )
    instance.personal_assistant = assistant
    instance.save(update_fields=["personal_assistant"])

    assistant_project = AssistantProject.objects.create(
        assistant=assistant,
        title=f"{assistant.name}'s Project",
        created_by=instance,
    )

    project = Project.objects.create(
        user=instance,
        title=f"{assistant.name} Project",
        assistant=assistant,
        assistant_project=assistant_project,
        project_type=ProjectType.ASSISTANT,
        status=ProjectStatus.ACTIVE,
    )

    session = ChatSession.objects.create(
        user=instance,
        assistant=assistant,
        project=project,
    )
    AssistantChatMessage.objects.create(
        session=session,
        role="assistant",
        content=f"Hello {instance.username}! I'm {assistant.name}.",
    )
