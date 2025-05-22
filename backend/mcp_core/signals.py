from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import NarrativeThread

@receiver([post_save, post_delete], sender=NarrativeThread)
def clear_thread_cache(sender, instance, **kwargs):
    cache.delete(f"thread_summary_{instance.id}")
    cache.delete(f"thread_replay_{instance.id}_0")
    cache.delete(f"thread_replay_{instance.id}_1")
    cache.delete("overview_threads")

