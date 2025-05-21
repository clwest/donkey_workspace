from django.db import models

class NarrativeEvent(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    linked_story = models.ForeignKey(
        'story.Story', on_delete=models.SET_NULL, null=True, blank=True, related_name='narrative_events'
    )
    linked_image = models.ForeignKey(
        'images.Image', on_delete=models.SET_NULL, null=True, blank=True, related_name='narrative_events'
    )
    linked_video = models.ForeignKey(
        'videos.Video', on_delete=models.SET_NULL, null=True, blank=True, related_name='narrative_events'
    )
    linked_character = models.ForeignKey(
        'characters.CharacterProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='narrative_events'
    )
    linked_tts = models.ForeignKey(
        'tts.StoryAudio', on_delete=models.SET_NULL, null=True, blank=True, related_name='narrative_events'
    )
    linked_memory = models.ForeignKey(
        'memory.MemoryEntry', on_delete=models.SET_NULL, null=True, blank=True, related_name='linked_narrative_events'
    )
    linked_assistant = models.ForeignKey(
        'assistants.Assistant', on_delete=models.SET_NULL, null=True, blank=True, related_name='linked_narrative_events'
    )
    narrative_thread = models.ForeignKey(
        'mcp_core.NarrativeThread', on_delete=models.SET_NULL, null=True, blank=True, related_name='events'
    )
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    auto_delegate = models.BooleanField(default=False)
    auto_reflect = models.BooleanField(default=False)
    auto_summarize = models.BooleanField(default=False)
    last_triggered = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title
