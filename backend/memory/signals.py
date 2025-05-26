from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps

from .models import MemoryEntry
from tasks import auto_tag_new_memory


@receiver(post_save, sender=MemoryEntry)
def trigger_auto_tag(sender, instance, created, **kwargs):
    if created:
        if not instance.related_project and instance.assistant and instance.assistant.current_project:
            instance.related_project = instance.assistant.current_project.project if hasattr(instance.assistant.current_project, "project") else instance.assistant.current_project
            try:
                instance.save(update_fields=["related_project"])
            except Exception:
                pass
        auto_tag_new_memory.delay(str(instance.id))

