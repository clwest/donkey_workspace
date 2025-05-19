from django.db import models
import uuid
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class MemoryEntry(models.Model):
    # 🔑 Identity & Timestamps
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 🧠 Core Content
    event = models.TextField()
    emotion = models.CharField(max_length=50, blank=True, null=True)
    importance = models.IntegerField(default=5)
    full_transcript = models.TextField(blank=True, null=True)
    is_conversation = models.BooleanField(default=False)

    # 🏷️ Metadata
    tags = models.ManyToManyField("mcp_core.Tag", blank=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    voice_clip = models.FileField(upload_to="memory_voices/", blank=True, null=True)

    summary = models.TextField(blank=True, null=True)
    document = models.ForeignKey(
        "intel_core.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="memory_entries",
    )
    type = models.CharField(max_length=100, default="general")
    auto_tagged = models.BooleanField(default=False)

    # 🔗 Relations (project, assistant, chat session)
    related_project = models.ForeignKey(
        "project.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="memory_entries",
    )
    assistant = models.ForeignKey(
        "assistants.Assistant",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="memories",
    )
    chat_session = models.ForeignKey(
        "assistants.ChatSession", on_delete=models.SET_NULL, null=True, blank=True
    )

    # 🧬 Embeddings
    embeddings = GenericRelation("embeddings.Embedding")

    context = models.ForeignKey(
        "mcp_core.MemoryContext",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="memory_entries",
    )

    narrative_thread = models.ForeignKey(
        "mcp_core.NarrativeThread",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="memories",
    )

    parent_memory = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="mutations",
    )

    # 🧑 Source Information
    source_role = models.CharField(
        max_length=50,
        choices=[
            ("user", "User"),
            ("assistant", "Assistant"),
            ("agent", "Agent"),
            ("system", "System"),
            ("external", "External"),
        ],
        default="assistant",
    )
    source_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="memory_entries",
    )

    linked_thought = models.ForeignKey(
        "assistants.AssistantThoughtLog",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_memories",
    )

    # 🧩 Polymorphic Link (replaces `linked_thought`)
    linked_content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    linked_object_id = models.UUIDField(null=True, blank=True)
    linked_object = GenericForeignKey("linked_content_type", "linked_object_id")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.timestamp} - {self.event[:30]}..."

    @property
    def source_name(self):
        if self.source_role == "user" and self.source_user:
            return self.source_user.name or self.source_user.username
        elif self.source_role == "assistant" and self.assistant:
            return self.assistant.name
        elif self.source_role == "agent" and hasattr(self.linked_object, "name"):
            return self.linked_object.name
        elif self.source_role == "system":
            return "System"
        elif self.source_role == "external":
            return "External Source"
        return "Unknown"


class MemoryChain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    memories = models.ManyToManyField(MemoryEntry, related_name="chains")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.title


class MemoryFeedback(models.Model):
    memory = models.ForeignKey(
        MemoryEntry, on_delete=models.CASCADE, related_name="feedback"
    )
    project = models.ForeignKey(
        "project.Project", null=True, blank=True, on_delete=models.SET_NULL
    )
    thought_log = models.ForeignKey(
        "assistants.AssistantThoughtLog",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    context_hint = models.TextField(blank=True)
    suggestion = models.TextField()
    explanation = models.TextField(blank=True)
    mutation_style = models.CharField(
        max_length=20,
        choices=[
            ("clarify", "Clarify"),
            ("shorten", "Shorten"),
            ("rephrase", "Rephrase"),
        ],
        null=True,
        blank=True,
    )
    submitted_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback on Memory {self.memory_id} by {self.submitted_by or 'anon'}"


# memory/models.py
class ReflectionFlag(models.Model):
    """Record a reflection flag on a memory entry with severity and reason."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    memory = models.ForeignKey(
        "memory.MemoryEntry", on_delete=models.CASCADE, related_name="flags"
    )
    reason = models.TextField()
    severity = models.CharField()

