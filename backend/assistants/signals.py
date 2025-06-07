from django.db.models.signals import post_save
from django.dispatch import receiver
from .models.reflection import AssistantReflectionLog
from .models.project import AssistantObjective
from project.models.task import ProjectTask
from project.models.core import Project
from .models.assistant import Assistant
from assistants.helpers.logging_helper import log_assistant_birth_event, reflect_on_birth


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
        core_project = Project.objects.filter(
            assistant_project=instance.project
        ).first()
        if core_project:
            ProjectTask.objects.create(
                project=core_project,
                title=instance.title or "Reflection Task",
                content=instance.summary,
            )


@receiver(post_save, sender=Assistant)
def record_birth_memory(sender, instance, created, **kwargs):
    """Log an origin memory when a spawned assistant is first created."""
    if created and instance.spawned_by and instance.created_by:
        if not instance.memories.filter(type="origin").exists():
            log_assistant_birth_event(instance, instance.created_by)
            reflect_on_birth(instance)
