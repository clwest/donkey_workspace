from django.db.models.signals import post_save
from django.dispatch import receiver
from .models.reflection import AssistantReflectionLog
from .models.project import AssistantObjective
from project.models.task import ProjectTask
from project.models.core import Project


@receiver(post_save, sender=AssistantReflectionLog)
def spawn_objectives_from_reflection(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.project:
        AssistantObjective.objects.create(
            project=instance.project,
            assistant=instance.assistant or instance.project.assistant,
            title=instance.title or "Reflection Objective",
            description=instance.summary,
            generated_from_reflection=instance,
        )
        core_project = Project.objects.filter(assistant_project=instance.project).first()
        if core_project:
            ProjectTask.objects.create(
                project=core_project,
                title=instance.title or "Reflection Task",
                content=instance.summary,
            )

