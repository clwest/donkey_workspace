from django.db import models


class InsightHub(models.Model):
    """Central symbolic exchange space for assistants."""

    name = models.CharField(max_length=150)
    focus_topics = models.JSONField()
    publishing_assistants = models.ManyToManyField("assistants.Assistant")
    active_tokens = models.ManyToManyField("agents.LoreToken", blank=True)
    memory_feed = models.ManyToManyField("agents.SwarmMemoryEntry", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class PerspectiveMergeEvent(models.Model):
    """Record of a reflective unification across assistants."""

    assistants_involved = models.ManyToManyField("assistants.Assistant")
    topic = models.TextField()
    contrasting_memories = models.ManyToManyField("agents.SwarmMemoryEntry", blank=True)
    resolution_summary = models.TextField()
    merged_insight = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class TimelineStitchLog(models.Model):
    """Log of narrative fragment stitching."""

    narrative_fragments = models.ManyToManyField("agents.SwarmMemoryEntry", blank=True)
    initiated_by = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    stitching_method = models.CharField(max_length=100)
    unified_thread_summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
