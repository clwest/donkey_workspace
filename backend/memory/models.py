from django.db import models
import uuid
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from agents.models import SwarmMemoryEntry

User = settings.AUTH_USER_MODEL


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
    title = models.CharField(max_length=200, blank=True, default="")
    document = models.ForeignKey(
        "intel_core.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="memory_entries",
    )
    type = models.CharField(max_length=100, default="general")
    auto_tagged = models.BooleanField(default=False)
    is_bookmarked = models.BooleanField(default=False)
    bookmark_label = models.CharField(max_length=100, blank=True, null=True)

    symbolic_change = models.BooleanField(default=False)
    related_campaign = models.ForeignKey(
        "agents.StabilizationCampaign",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="memory_entries",
    )
    anchor = models.ForeignKey(
        "memory.SymbolicMemoryAnchor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="memories",
    )

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

    linked_agents = models.ManyToManyField(
        "agents.Agent", blank=True, related_name="memory_entries"
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
    thread = models.ForeignKey(
        "mcp_core.NarrativeThread",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="thread_memories",
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
        related_name="direct_linked_memories",
    )

    # 🧩 Polymorphic Link (replaces `linked_thought`)
    linked_content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    # CharField allows linking to objects with either UUID or integer primary keys
    linked_object_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
    )
    linked_object = GenericForeignKey("linked_content_type", "linked_object_id")
    tool_response = models.JSONField(null=True, blank=True)

    # 📈 Scoring & Context
    relevance_score = models.FloatField(default=0.0)
    context_tags = models.JSONField(default=list, blank=True)
    triggered_by = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.timestamp} - {self.event[:30]}..."

    def generate_memory_title(self):
        if self.title:
            return self.title
        if self.summary:
            return self.summary[:60]
        return self.event[:60]

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.generate_memory_title()
        super().save(*args, **kwargs)

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

    def get_content_preview(self) -> str:
        """Return a short preview string for UI display."""
        content = self.event or self.summary or self.full_transcript
        if content:
            return content[:200]

        tags = list(self.tags.all()[:3])
        if tags:
            tag_str = ", ".join(f"#{t.slug}" for t in tags)
            return f"\U0001f9e0 Tags: {tag_str}"
        if self.session_id:
            return f"\ud83d\udd04 Created by reflection for session {self.session_id}"
        return "(No content available)"

    @property
    def content_preview(self) -> str:
        return self.get_content_preview()


class MemoryChain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    memories = models.ManyToManyField(MemoryEntry, related_name="chains")
    thread = models.ForeignKey(
        "mcp_core.NarrativeThread",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="chains",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    context_tags = models.JSONField(default=list, blank=True)
    task_type = models.CharField(max_length=100, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)

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


class SimulatedMemoryFork(models.Model):
    """Store hypothetical outcomes for alternate memory scenarios."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_memory = models.ForeignKey(
        MemoryEntry, on_delete=models.CASCADE, related_name="simulated_forks"
    )
    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="simulated_memory_forks",
    )
    simulated_outcome = models.TextField()
    hypothetical_action = models.TextField(blank=True, null=True)
    reason_for_simulation = models.TextField(blank=True)
    thought_log = models.ForeignKey(
        "assistants.AssistantThoughtLog",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="memory_forks",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Fork of {self.original_memory_id} by {self.assistant.name}"


class MemoryBranch(models.Model):
    """Branch speculative timeline from a SwarmMemoryEntry."""

    root_entry = models.ForeignKey(
        "agents.SwarmMemoryEntry",
        on_delete=models.CASCADE,
        related_name="branches",
    )
    fork_reason = models.TextField()
    speculative_outcome = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class SharedMemoryPool(models.Model):
    """Collection of shared key-value data accessible by multiple assistants."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    glossary_guidance = models.TextField(blank=True, default="")
    assistants = models.ManyToManyField(
        "assistants.Assistant", blank=True, related_name="shared_pools"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SharedMemoryEntry(models.Model):
    """Key-value pair stored within a SharedMemoryPool."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pool = models.ForeignKey(
        SharedMemoryPool, on_delete=models.CASCADE, related_name="entries"
    )
    key = models.CharField(max_length=255)
    value = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        "assistants.Assistant", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("pool", "key")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.key}: {self.value}"


class BraidedMemoryStrand(models.Model):
    """Merge and align symbolic memories from alternate timelines."""

    primary_assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="braided_strands"
    )
    alternate_sources = models.ManyToManyField(
        "agents.SwarmMemoryEntry", related_name="braided_into", blank=True
    )
    integration_notes = models.TextField(blank=True)
    symbolic_alignment_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class ContinuityAnchorPoint(models.Model):
    """Symbolic anchor ensuring identity coherence across timelines."""

    label = models.CharField(max_length=100)
    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="continuity_anchors",
    )
    anchor_memory = models.ForeignKey(
        "agents.SwarmMemoryEntry",
        on_delete=models.CASCADE,
        related_name="anchor_points",
    )
    mythic_tag = models.CharField(max_length=100)
    symbolic_signature = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class SymbolicMemoryAnchor(models.Model):
    """Anchor term used for symbolic continuity across content."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True)
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    glossary_guidance = models.TextField(blank=True, default="")
    is_focus_term = models.BooleanField(default=False)
    tags = models.ManyToManyField("mcp_core.Tag", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["slug"]

    def __str__(self):
        return self.label


class MemoryEmbeddingFailureLog(models.Model):
    """Log failed embedding attempts for later analysis and retry."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_set = models.ForeignKey(
        "intel_core.DocumentSet",
        on_delete=models.CASCADE,
        related_name="embedding_failures",
    )
    chunk_index = models.IntegerField()
    text = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class MemoryEntropyAudit(models.Model):
    """Record entropy metrics for an assistant's memory chain."""

    chain = models.ForeignKey(
        "assistants.AssistantMemoryChain",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entropy_audits",
    )
    entropy_score = models.FloatField()
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class MemoryMergeSuggestion(models.Model):
    """Suggest merging two memories to reduce symbolic drift."""

    entry_a = models.ForeignKey(
        MemoryEntry, on_delete=models.CASCADE, related_name="merge_a"
    )
    entry_b = models.ForeignKey(
        MemoryEntry, on_delete=models.CASCADE, related_name="merge_b"
    )
    merge_reason = models.TextField()
    suggested_by = models.ForeignKey(
        "assistants.Assistant", on_delete=models.SET_NULL, null=True, blank=True
    )
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class GlossaryRetryLog(models.Model):
    """Record glossary retry attempts and their outcomes."""

    anchor = models.ForeignKey(
        SymbolicMemoryAnchor, on_delete=models.SET_NULL, null=True, blank=True
    )
    question = models.TextField()
    first_response = models.TextField()
    retry_response = models.TextField(blank=True, null=True)
    glossary_chunks = models.JSONField(default=list, blank=True)
    guidance_injected = models.BooleanField(default=False)
    retried = models.BooleanField(default=False)
    score_diff = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
